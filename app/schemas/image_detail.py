from datetime import datetime

from pydantic import BaseModel, Field

from app.core.logging import logger


logger.info("Image detail schemas loaded")


class TransformationSummary(BaseModel):

    id: int

    format: str

    width: int = Field(gt=0)

    height: int = Field(gt=0)

    file_size: int = Field(gt=0)

    storage_key: str

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class ImageDetailResponse(BaseModel):

    id: int

    original_filename: str

    storage_key: str

    mime_type: str

    format: str

    width: int = Field(gt=0)

    height: int = Field(gt=0)

    file_size: int = Field(gt=0)

    created_at: datetime

    transformations: list[TransformationSummary] = Field(
        default_factory=list
    )

    model_config = {
        "from_attributes": True,
    }