import mimetypes

from app.core.logging import logger


logger.info("File utils loaded")


def get_mime_type(filename: str) -> str:

    logger.info(
        "Getting MIME type | filename=%s",
        filename,
    )

    mime_type, _ = mimetypes.guess_type(
        filename
    )

    return mime_type or "application/octet-stream"