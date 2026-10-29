from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.image import router as image_router
from app.core.logging import logger

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
  logger.info("Starting Cloud Image Processing Service | version=1.0.0")
  yield
  logger.info("Shutting down Cloud Image Processing Service")

app = FastAPI(
    title="Cloud Image Processing Service",
    version="1.0.0",
    description="Cloud-based image upload, storage and transformation API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(health_router)
app.include_router(auth_router)
app.include_router(image_router)



@app.get("/")
def root():
    return {
        "service": "Cloud Image Processing Service",
        "version": "1.0.0",
        "status": "running",
    }