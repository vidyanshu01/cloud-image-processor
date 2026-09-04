from PIL import Image, UnidentifiedImageError

from app.core.constants import (
    ALLOWED_IMAGE_TYPES,
    MAX_IMAGE_HEIGHT,
    MAX_IMAGE_PIXELS,
    MAX_IMAGE_SIZE,
    MAX_IMAGE_WIDTH,
)
from app.core.logging import logger

logger.info("Image validator loaded")


def validate_file_size(file_size: int) -> None:
    """
    Validate uploaded image file size.
    """

    logger.info(
        "Validating file size | size=%s bytes",
        file_size,
    )

    if file_size > MAX_IMAGE_SIZE:
        logger.warning(
            "File size exceeded limit | size=%s",
            file_size,
        )

        raise ValueError(
            "Image size must not exceed 10MB."
        )

    logger.info("File size validation successful")


def validate_mime_type(
    content_type: str | None,
) -> None:
    """
    Validate uploaded image MIME type.
    """

    logger.info(
        "Validating MIME type | type=%s",
        content_type,
    )

    if content_type not in ALLOWED_IMAGE_TYPES:
        logger.warning(
            "Unsupported MIME type | type=%s",
            content_type,
        )

        raise ValueError(
            "Unsupported image format."
        )

    logger.info("MIME type validation successful")


def validate_image(
    file_path: str,
) -> Image.Image:
    """
    Verify that the uploaded file is a valid image.
    """

    logger.info(
        "Validating image file | path=%s",
        file_path,
    )

    try:
        image = Image.open(file_path)

        # Verify file integrity without loading the entire image.
        image.verify()

        # Reopen because verify() invalidates the image object.
        image = Image.open(file_path)

        logger.info(
            "Image validation successful | "
            "format=%s | width=%s | height=%s",
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
            "Invalid or corrupted image | path=%s",
            file_path,
        )

        raise ValueError(
            "Invalid or corrupted image file."
        ) from exc


def validate_dimensions(
    width: int,
    height: int,
) -> None:
    """
    Validate image width and height limits.
    """

    logger.info(
        "Validating dimensions | width=%s | height=%s",
        width,
        height,
    )

    if width > MAX_IMAGE_WIDTH:
        logger.warning(
            "Image width exceeded limit | width=%s | max=%s",
            width,
            MAX_IMAGE_WIDTH,
        )

        raise ValueError(
            "Image width is too large."
        )

    if height > MAX_IMAGE_HEIGHT:
        logger.warning(
            "Image height exceeded limit | height=%s | max=%s",
            height,
            MAX_IMAGE_HEIGHT,
        )

        raise ValueError(
            "Image height is too large."
        )

    logger.info("Dimension validation successful")


def validate_pixels(
    width: int,
    height: int,
) -> None:
    """
    Validate total image pixel count.
    """

    pixels = width * height

    logger.info(
        "Validating pixels | pixels=%s",
        pixels,
    )

    if pixels > MAX_IMAGE_PIXELS:
        logger.warning(
            "Pixel limit exceeded | pixels=%s | max=%s",
            pixels,
            MAX_IMAGE_PIXELS,
        )

        raise ValueError(
            "Image contains too many pixels."
        )

    logger.info("Pixel validation successful")


def validate_uploaded_image(
    file_path: str,
    file_size: int,
    content_type: str | None,
) -> dict:
    """
    Run all validations for an uploaded image.
    """

    logger.info(
        "Uploaded image validation started"
    )

    # 1. File size validation
    validate_file_size(file_size)

    # 2. MIME type validation
    validate_mime_type(content_type)

    # 3. Actual image integrity validation
    image = validate_image(file_path)

    # 4. Dimension validation
    validate_dimensions(
        image.width,
        image.height,
    )

    # 5. Pixel count validation
    validate_pixels(
        image.width,
        image.height,
    )

    metadata = {
        "format": image.format,
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
    }

    logger.info(
        "Uploaded image validation completed | "
        "format=%s | width=%s | height=%s",
        image.format,
        image.width,
        image.height,
    )

    return metadata