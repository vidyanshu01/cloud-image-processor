from typing import Literal

from pydantic import BaseModel, Field

from app.core.logging import logger


logger.info("Image query schema loaded")


class ImageQueryParams(BaseModel):

    page: int = Field(
        default=1,
        ge=1,
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    format: str | None = Field(
        default=None,
        min_length=2,
        max_length=10,
    )

    sort: Literal[
        "newest",
        "oldest",
        "largest",
        "smallest",
    ] = "newest"