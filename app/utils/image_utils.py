from io import BytesIO

from PIL import Image, UnidentifiedImageError

from app.core.logging import logger


logger.info("Image utils loaded")


def validate_image(content: bytes):

    logger.info(
        "Image validation started | size=%s",
        len(content),
    )

    try:

        image = Image.open(
            BytesIO(content)
        )

        image.verify()

        image = Image.open(
            BytesIO(content)
        )

        logger.info(
            "Image validation successful | format=%s | width=%s | height=%s",
            image.format,
            image.width,
            image.height,
        )

        return image

    except (
        UnidentifiedImageError,
        OSError,
    ) as exc:

        logger.warning(
            "Invalid or corrupted image"
        )

        raise ValueError(
            "Invalid or corrupted image file."
        ) from exc