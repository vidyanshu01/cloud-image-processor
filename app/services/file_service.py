from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.image import Image
from app.models.transformation import ImageTransformation
from app.storage import storage
from app.core.logging import logger


logger.info("File service loaded")


class ImageFileService:
    """
    Service responsible for generating secure access URLs
    for original and transformed images stored in AWS S3.
    """

    def get_original_file(
        self,
        db: Session,
        image_id: int,
        user_id: int,
    ) -> dict:
        """
        Generate a temporary presigned URL for an original image.
        """

        logger.info(
            "Getting original image file | image_id=%s | user_id=%s",
            image_id,
            user_id,
        )

        image = (
            db.query(Image)
            .filter(
                Image.id == image_id,
                Image.user_id == user_id,
            )
            .first()
        )

        if not image:
            logger.warning(
                "Original image not found | image_id=%s | user_id=%s",
                image_id,
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found.",
            )

        try:
            url = storage.download_url(
                storage_key=image.storage_key,
                expires=3600,
            )

        except Exception as exc:
            logger.exception(
                "Failed to generate original image URL | "
                "image_id=%s | user_id=%s",
                image_id,
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image file not found.",
            ) from exc

        logger.info(
            "Original image URL generated successfully | "
            "image_id=%s | user_id=%s",
            image_id,
            user_id,
        )

        return {
            "url": url,
            "mime_type": image.mime_type,
            "expires_in": 3600,
        }

    def get_transformed_file(
        self,
        db: Session,
        transformation_id: int,
        user_id: int,
    ) -> dict:
        """
        Generate a temporary presigned URL for a transformed image.
        """

        logger.info(
            "Getting transformed image file | "
            "transformation_id=%s | user_id=%s",
            transformation_id,
            user_id,
        )

        transformation = (
            db.query(ImageTransformation)
            .filter(
                ImageTransformation.id == transformation_id,
                ImageTransformation.user_id == user_id,
            )
            .first()
        )

        if not transformation:
            logger.warning(
                "Transformation not found | "
                "transformation_id=%s | user_id=%s",
                transformation_id,
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transformation not found.",
            )

        try:
            url = storage.download_url(
                storage_key=transformation.storage_key,
                expires=3600,
            )

        except Exception as exc:
            logger.exception(
                "Failed to generate transformed image URL | "
                "transformation_id=%s | user_id=%s",
                transformation_id,
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transformed image file not found.",
            ) from exc

        logger.info(
            "Transformed image URL generated successfully | "
            "transformation_id=%s | user_id=%s",
            transformation_id,
            user_id,
        )

        return {
            "url": url,
            "mime_type": transformation.mime_type,
            "expires_in": 3600,
        }