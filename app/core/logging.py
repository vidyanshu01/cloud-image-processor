import logging
from datetime import datetime
from pathlib import Path



LOG_DIR = Path("app/logs")

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


LOG_FILE = LOG_DIR / (
    f"app_{datetime.now():%Y-%m-%d}.log"
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(name)s | "
        "%(filename)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("app")