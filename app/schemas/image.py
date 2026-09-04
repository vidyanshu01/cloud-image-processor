from datetime import datetime

from pydantic import BaseModel, Field

from app.core.logging import logger


logger.info("Image schemas loaded")


class ImageResponse(BaseModel):

    id: int

    original_filename: str = Field(
        min_length=1,
        max_length=255,
    )

    mime_type: str

    format: str

    width: int = Field(
        gt=0,
    )

    height: int = Field(
        gt=0,
    )

    file_size: int = Field(
        gt=0,
    )

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class ImageListResponse(BaseModel):

    page: int = Field(
        ge=1,
    )

    limit: int = Field(
        ge=1,
        le=100,
    )

    total: int = Field(
        ge=0,
    )

    total_pages: int = Field(
        ge=0,
    )

    items: list[ImageResponse]


class FileAccessResponse(BaseModel):

    url: str

    mime_type: str

    expires_in: int = Field(
        gt=0,
    )