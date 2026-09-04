from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import health
from app.api.auth import router as auth_router
from app.api.image import router as image_router

from app.core.config import settings
from app.core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(
        "Starting %s | version=%s",
        settings.APP_NAME,
        settings.APP_VERSION,
    )

    yield

    logger.info(
        "Shutting down %s",
        settings.APP_NAME,
    )


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Cloud-based image upload, storage, "
        "retrieval, and transformation service."
    ),
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


app.include_router(
    health.router,
)

app.include_router(
    auth_router,
)

app.include_router(
    image_router,
)


@app.get(
    "/",
    tags=["Root"],
)
def root():

    logger.info(
        "Root endpoint requested"
    )

    return {
        "message": "Welcome to CloudImage API",
        "status": "running",
        "version": settings.APP_VERSION,
    }