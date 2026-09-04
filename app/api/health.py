from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import logger


router = APIRouter(
    prefix="/api/v1/health",
    tags=["Health"],
)


@router.get("")
def health_check():
    logger.info("Health check requested")

    return {
        "status": "healthy",
        "service": "Cloud Image API",
    }


@router.get("/db")
def database_health(
    db: Session = Depends(get_db),
):
    try:

        db.execute(
            text("SELECT 1")
        )

        logger.info(
            "Database health check successful"
        )

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as exc:

        logger.exception(
            "Database health check failed"
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
            },
        ) from exc