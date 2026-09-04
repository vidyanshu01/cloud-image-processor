from pydantic import BaseModel, Field

from app.core.logging import logger


logger.info("Image file response schema loaded")


class ImageFileInfo(BaseModel):

    filename: str = Field(
        min_length=1,
        max_length=255,
    )

    mime_type: str = Field(
        min_length=1,
        max_length=100,
    )

    size: int = Field(
        gt=0,
    )

    width: int = Field(
        gt=0,
    )

    height: int = Field(
        gt=0,
    )