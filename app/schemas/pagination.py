from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from app.core.logging import logger


logger.info("Pagination schemas loaded")


T = TypeVar("T")


class PaginationMeta(BaseModel):

    page: int = Field(
        ge=1
    )

    limit: int = Field(
        ge=1,
        le=100
    )

    total: int = Field(
        ge=0
    )

    total_pages: int = Field(
        ge=0
    )


class PaginationResponse(
    BaseModel,
    Generic[T]
):

    items: list[T]

    pagination: PaginationMeta