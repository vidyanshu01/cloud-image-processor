import io
import time
import uuid

from PIL import (
    Image as PILImage,
    ImageOps,
    ImageDraw,
    ImageFont,
)

from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.image import Image
from app.models.transformation import ImageTransformation
from app.schemas.transformation import TransformationRequest
from app.storage import storage
from app.utils.hash_utils import create_transformation_hash


logger.info("Transformation service loaded")


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

    # 1. Create transformation hash
    transformation_hash = create_transformation_hash(
        transformations
    )

    # 2. Check cache
    cached_result = db.query(
        ImageTransformation
    ).filter(
        ImageTransformation.image_id == image_record.id,
        ImageTransformation.user_id == user_id,
        ImageTransformation.transformation_hash
        == transformation_hash,
    ).first()

    if cached_result:

        logger.info(
            "Transformation cache hit | image_id=%s",
            image_record.id,
        )

        return cached_result, True

    # 3. Download original image from R2
    try:

        logger.info(
            "Downloading original image from R2 | key=%s",
            image_record.storage_key,
        )

        image_bytes = storage.download_file(
            image_record.storage_key
        )

        original_image = PILImage.open(
            io.BytesIO(image_bytes)
        )

        original_image.load()

    except Exception as exc:

        logger.exception(
            "Failed to load original image | image_id=%s",
            image_record.id,
        )

        raise ValueError(
            "Unable to load original image"
        ) from exc

    # 4. Apply transformations
    service = ImageTransformationService()

    transformed_image = service.apply_transformation(
        original_image,
        transformations,
    )

    # 5. Determine output format
    output_format = (
        transformations.format
        or image_record.format
    ).upper()

    if output_format == "JPG":
        output_format = "JPEG"

    extension = (
        "jpg"
        if output_format == "JPEG"
        else output_format.lower()
    )

    mime_type = f"image/{'jpeg' if output_format == 'JPEG' else extension}"

    # 6. Prepare image for output format
    transformed_image = service.prepare_for_format(
        transformed_image,
        output_format,
    )

    # 7. Convert image to bytes
    output_buffer = io.BytesIO()

    save_kwargs = {}

    if transformations.quality:
        save_kwargs["quality"] = transformations.quality

    if output_format == "JPEG":
        save_kwargs["optimize"] = True

    transformed_image.save(
        output_buffer,
        format=output_format,
        **save_kwargs,
    )

    output_buffer.seek(0)

    output_bytes = output_buffer.getvalue()

    # 8. Generate R2 storage key
    storage_key = (
        f"users/{user_id}/"
        f"transformations/"
        f"{uuid.uuid4()}.{extension}"
    )

    # 9. Upload transformed image to R2
    try:

        logger.info(
            "Uploading transformed image to R2 | key=%s",
            storage_key,
        )

        storage.upload_bytes(
            data=output_bytes,
            storage_key=storage_key,
            content_type=mime_type,
        )

    except Exception as exc:

        logger.exception(
            "Failed to upload transformed image"
        )

        raise ValueError(
            "Unable to save transformed image"
        ) from exc

    # 10. Save transformation metadata
    transformation = ImageTransformation(
        image_id=image_record.id,
        user_id=user_id,
        transformation_hash=transformation_hash,
        storage_key=storage_key,
        format=output_format,
        mime_type=mime_type,
        width=transformed_image.width,
        height=transformed_image.height,
        file_size=len(output_bytes),
    )

    try:

        db.add(transformation)
        db.commit()
        db.refresh(transformation)

    except Exception:

        db.rollback()

        try:
            storage.delete_file(
                storage_key
            )
        except Exception:
            logger.exception(
                "Failed to cleanup R2 file"
            )

        raise

    elapsed = time.perf_counter() - start_time

    logger.info(
        "Transformation completed | image_id=%s | time=%.3fs",
        image_record.id,
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
            "Applying crop | x=%s | y=%s | width=%s | height=%s",
            x,
            y,
            width,
            height,
        )

        right = x + width
        bottom = y + height

        if right > image.width:
            raise ValueError(
                "Crop exceeds image width"
            )

        if bottom > image.height:
            raise ValueError(
                "Crop exceeds image height"
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

        grayscale = ImageOps.grayscale(
            image
        )

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

        draw = ImageDraw.Draw(
            overlay
        )

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