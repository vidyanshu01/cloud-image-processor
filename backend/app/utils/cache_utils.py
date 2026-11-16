import hashlib

from app.core.logging import logger


logger.info("Cache utils loaded")


def generate_etag(
    storage_key: str,
    updated_at: str | None = None,
) -> str:

    logger.info(
        "Generating ETag | storage_key=%s",
        storage_key,
    )

    value = f"{storage_key}:{updated_at or ''}"

    etag = hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()

    logger.info("ETag generated")

    return etag