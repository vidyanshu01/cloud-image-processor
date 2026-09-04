import io
import time

from PIL import Image as PILImage
from PIL import ImageDraw, ImageFont, ImageOps
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.image import Image
from app.models.transformation import ImageTransformation
from app.schemas.transformation import TransformationRequest
from app.storage import storage
from app.utils.hash_utils import create_transformation_hash

from app.utils.storage_key import (
    generate_transformation_storage_key,
)


logger.info("Transformation service loaded")


OUTPUT_FORMATS = {
    "JPEG": {
        "extension": "jpg",
        "mime_type": "image/jpeg",
    },
    "JPG": {
        "extension": "jpg",
        "mime_type": "image/jpeg",
    },
    "PNG": {
        "extension": "png",
        "mime_type": "image/png",
    },
    "WEBP": {
        "extension": "webp",
        "mime_type": "image/webp",
    },
    "GIF": {
        "extension": "gif",
        "mime_type": "image/gif",
    },
}


def process_transformation(
    db: Session,
    image_record: Image,
    user_id: int,
    transformations: TransformationRequest,
) -> tuple[ImageTransformation, bool]:

    start_time = time.perf_counter()

    logger.info(
        "Transformation started | image_id=%s | user_id=%s",
        image_record.id,
        user_id,
    )

    transformation_hash = create_transformation_hash(
        transformations
    )

    logger.info(
        "Transformation hash generated | image_id=%s",
        image_record.id,
    )

    cached_result = (
        db.query(ImageTransformation)
        .filter(
            ImageTransformation.image_id == image_record.id,
            ImageTransformation.user_id == user_id,
            ImageTransformation.transformation_hash
            == transformation_hash,
        )
        .first()
    )

    if cached_result:
        logger.info(
            "Transformation cache hit | "
            "image_id=%s | transformation_id=%s",
            image_record.id,
            cached_result.id,
        )

        return cached_result, True

    logger.info(
        "Transformation cache miss | image_id=%s",
        image_record.id,
    )

    try:
        logger.info(
            "Downloading original image from S3 | key=%s",
            image_record.storage_key,
        )

        image_bytes = storage.download(
            image_record.storage_key
        )

        original_image = PILImage.open(
            io.BytesIO(image_bytes)
        )

        original_image.load()

    except Exception as exc:
        logger.exception(
            "Failed to load original image from S3 | "
            "image_id=%s",
            image_record.id,
        )

        raise ValueError(
            "Unable to load original image."
        ) from exc

    service = ImageTransformationService()

    try:
        transformed_image = service.apply_transformation(
            original_image,
            transformations,
        )

    except ValueError:
        logger.exception(
            "Transformation failed | image_id=%s",
            image_record.id,
        )

        original_image.close()
        raise

    finally:
        original_image.close()

    output_format = (
        transformations.format
        or image_record.format
    ).upper()

    format_config = OUTPUT_FORMATS.get(output_format)

    if format_config is None:
        logger.warning(
            "Unsupported output format | format=%s",
            output_format,
        )

        transformed_image.close()

        raise ValueError(
            "Unsupported output format."
        )

    extension = format_config["extension"]
    mime_type = format_config["mime_type"]

    logger.info(
        "Output format determined | "
        "format=%s | extension=%s",
        output_format,
        extension,
    )

    try:
        transformed_image = service.prepare_for_format(
            transformed_image,
            output_format,
        )

    except Exception as exc:
        logger.exception(
            "Failed to prepare image for output | "
            "image_id=%s | format=%s",
            image_record.id,
            output_format,
        )

        transformed_image.close()

        raise ValueError(
            "Unable to prepare transformed image."
        ) from exc

    transformed_width = transformed_image.width
    transformed_height = transformed_image.height

    logger.info(
        "Transformed dimensions determined | "
        "image_id=%s | width=%s | height=%s",
        image_record.id,
        transformed_width,
        transformed_height,
    )

    output_buffer = io.BytesIO()

    save_kwargs = {}

    if transformations.quality is not None:
        save_kwargs["quality"] = transformations.quality

    if output_format == "JPEG":
        save_kwargs["optimize"] = True

    try:
        transformed_image.save(
            output_buffer,
            format=output_format,
            **save_kwargs,
        )

        output_bytes = output_buffer.getvalue()

    except Exception as exc:
        logger.exception(
            "Failed to encode transformed image | "
            "image_id=%s",
            image_record.id,
        )

        raise ValueError(
            "Unable to encode transformed image."
        ) from exc

    finally:
        output_buffer.close()
        transformed_image.close()

    logger.info(
        "Transformation encoded | "
        "image_id=%s | size=%s bytes",
        image_record.id,
        len(output_bytes),
    )

    storage_key = generate_transformation_storage_key(
    user_id=user_id,
    extension=extension,
    )
    
    logger.info(
        "Transformation S3 key generated | key=%s",
        storage_key,
    )

    try:
        storage.upload_bytes(
            data=output_bytes,
            storage_key=storage_key,
            content_type=mime_type,
        )

        logger.info(
            "Transformed image uploaded to S3 | key=%s",
            storage_key,
        )

    except Exception as exc:
        logger.exception(
            "Failed to upload transformed image to S3 | "
            "key=%s",
            storage_key,
        )

        raise ValueError(
            "Unable to save transformed image."
        ) from exc
        
    transformation = ImageTransformation(
        image_id=image_record.id,
        user_id=user_id,
        transformation_hash=transformation_hash,
        storage_key=storage_key,
        format=output_format,
        mime_type=mime_type,
        width=transformed_width,
        height=transformed_height,
        file_size=len(output_bytes),
    )

    try:
        db.add(transformation)
        db.commit()
        db.refresh(transformation)

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Failed to save transformation metadata | "
            "image_id=%s",
            image_record.id,
        )

        try:
            storage.delete(storage_key)

            logger.info(
                "S3 transformation cleanup successful | key=%s",
                storage_key,
            )

        except Exception:
            logger.exception(
                "Failed to cleanup S3 transformation | key=%s",
                storage_key,
            )

        raise ValueError(
            "Unable to save transformation metadata."
        ) from exc

    elapsed = time.perf_counter() - start_time

    logger.info(
        "Transformation completed | "
        "image_id=%s | transformation_id=%s | "
        "time=%.3fs",
        image_record.id,
        transformation.id,
        elapsed,
    )

    return transformation, False


class ImageTransformationService:

    def resize(
        self,
        image: PILImage.Image,
        width: int,
        height: int,
    ) -> PILImage.Image:

        logger.info(
            "Applying resize | width=%s | height=%s",
            width,
            height,
        )

        return image.resize(
            (width, height),
            PILImage.Resampling.LANCZOS,
        )

    def crop(
        self,
        image: PILImage.Image,
        width: int,
        height: int,
        x: int,
        y: int,
    ) -> PILImage.Image:

        logger.info(
            "Applying crop | "
            "x=%s | y=%s | width=%s | height=%s",
            x,
            y,
            width,
            height,
        )

        right = x + width
        bottom = y + height

        if right > image.width:
            raise ValueError(
                "Crop exceeds image width."
            )

        if bottom > image.height:
            raise ValueError(
                "Crop exceeds image height."
            )

        return image.crop(
            (x, y, right, bottom)
        )

    def rotate(
        self,
        image: PILImage.Image,
        angle: int,
    ) -> PILImage.Image:

        logger.info(
            "Applying rotation | angle=%s",
            angle,
        )

        return image.rotate(
            angle,
            expand=True,
        )

    def flip(
        self,
        image: PILImage.Image,
    ) -> PILImage.Image:

        logger.info("Applying vertical flip")

        return ImageOps.flip(image)

    def mirror(
        self,
        image: PILImage.Image,
    ) -> PILImage.Image:

        logger.info("Applying horizontal mirror")

        return ImageOps.mirror(image)

    def grayscale(
        self,
        image: PILImage.Image,
    ) -> PILImage.Image:

        logger.info("Applying grayscale filter")

        return ImageOps.grayscale(
            image
        ).convert("RGB")

    def sepia(
        self,
        image: PILImage.Image,
    ) -> PILImage.Image:

        logger.info("Applying sepia filter")

        image = image.convert("RGB")

        grayscale = ImageOps.grayscale(image)

        return ImageOps.colorize(
            grayscale,
            black=(50, 30, 20),
            white=(255, 240, 210),
        )

    def watermark(
        self,
        image: PILImage.Image,
        text: str,
    ) -> PILImage.Image:

        logger.info("Applying watermark")

        image = image.convert("RGBA")

        overlay = PILImage.new(
            "RGBA",
            image.size,
            (255, 255, 255, 0),
        )

        draw = ImageDraw.Draw(overlay)

        font_size = max(
            20,
            image.width // 30,
        )

        try:
            font = ImageFont.truetype(
                "arial.ttf",
                font_size,
            )

        except OSError:
            font = ImageFont.load_default()

        margin = 20

        draw.text(
            (
                image.width - margin,
                image.height - margin,
            ),
            text=text,
            font=font,
            fill=(255, 255, 255, 180),
            anchor="rs",
        )

        return PILImage.alpha_composite(
            image,
            overlay,
        )

    def prepare_for_format(
        self,
        image: PILImage.Image,
        image_format: str,
    ) -> PILImage.Image:

        if image_format in {"JPEG", "JPG"}:
            if image.mode in {
                "RGBA",
                "LA",
                "P",
            }:
                image = image.convert("RGB")

        return image

    def apply_transformation(
        self,
        image: PILImage.Image,
        transformation: TransformationRequest,
    ) -> PILImage.Image:

        logger.info(
            "Applying requested transformations"
        )

        image = image.convert("RGB")

        if transformation.resize:
            image = self.resize(
                image,
                transformation.resize.width,
                transformation.resize.height,
            )

        if transformation.crop:
            image = self.crop(
                image,
                transformation.crop.width,
                transformation.crop.height,
                transformation.crop.x,
                transformation.crop.y,
            )

        if transformation.rotate:
            image = self.rotate(
                image,
                transformation.rotate,
            )

        if transformation.flip:
            image = self.flip(image)

        if transformation.mirror:
            image = self.mirror(image)

        if transformation.watermark:
            image = self.watermark(
                image,
                transformation.watermark,
            )

        if transformation.filter:
            if transformation.filter.grayscale:
                image = self.grayscale(image)

            if transformation.filter.sepia:
                image = self.sepia(image)

        return image