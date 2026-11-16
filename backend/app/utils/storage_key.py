from uuid import uuid4

from app.core.logging import logger


logger.info("Storage key utility loaded")


def generate_storage_key(
    user_id: int,
    extension: str,
) -> str:
    """
    Generate a unique S3 storage key for an original image.
    """

    extension = extension.lower().lstrip(".")

    filename = f"{uuid4()}.{extension}"

    storage_key = (
        f"users/{user_id}/images/{filename}"
    )

    logger.info(
        "Image storage key generated | "
        "user_id=%s | key=%s",
        user_id,
        storage_key,
    )

    return storage_key


def generate_transformation_storage_key(
    user_id: int,
    extension: str,
) -> str:
    """
    Generate a unique S3 storage key for a transformed image.
    """

    extension = extension.lower().lstrip(".")

    filename = f"{uuid4()}.{extension}"

    storage_key = (
        f"users/{user_id}/transformations/{filename}"
    )

    logger.info(
        "Transformation storage key generated | "
        "user_id=%s | key=%s",
        user_id,
        storage_key,
    )

    return storage_key