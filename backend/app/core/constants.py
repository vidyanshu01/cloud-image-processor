from app.core.logging import logger


MAX_IMAGE_SIZE = 10 * 1024 * 1024

MAX_IMAGE_WIDTH = 10_000

MAX_IMAGE_HEIGHT = 10_000

MAX_IMAGE_PIXELS = 50_000_000


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


logger.info(
    "Image constants loaded | max_size=%s MB | max_pixels=%s",
    MAX_IMAGE_SIZE // (1024 * 1024),
    MAX_IMAGE_PIXELS,
)