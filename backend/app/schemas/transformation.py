from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.core.logging import logger


logger.info("Transformation schemas loaded")


class ResizeOptions(BaseModel):

    width: int = Field(
        gt=0,
        le=10000,
    )

    height: int = Field(
        gt=0,
        le=10000,
    )


class CropOptions(BaseModel):

    width: int = Field(
        gt=0,
        le=10000,
    )

    height: int = Field(
        gt=0,
        le=10000,
    )

    x: int = Field(
        ge=0,
    )

    y: int = Field(
        ge=0,
    )


class FilterOptions(BaseModel):

    grayscale: bool = False

    sepia: bool = False


class TransformationRequest(BaseModel):

    resize: ResizeOptions | None = None

    crop: CropOptions | None = None

    rotate: int = Field(
        default=0,
        ge=-360,
        le=360,
    )

    flip: bool = False

    mirror: bool = False

    watermark: str | None = None

    filter: FilterOptions | None = None

    format: Literal[
        "JPEG",
        "PNG",
        "WEBP",
        "JPG",
        "GIF",
    ] | None = None

    quality:int = Field(
        default=85,
        ge=1,
        le=100,
    )


class TransformationResponse(BaseModel):

    id: int

    image_id: int

    storage_key: str

    format: str

    mime_type: str

    width: int

    height: int

    file_size: int

    cached: bool

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }