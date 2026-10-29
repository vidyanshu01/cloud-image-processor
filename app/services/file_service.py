from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.image import Image
from app.models.transformation import ImageTransformation
from app.storage import storage
from app.core.logging import logger


logger.info("File service loaded")


class ImageFileService:
    """
    Service responsible for generating secure presigned URLs
    for original and transformed images stored in S3-compatible storage.
    """

    def get_original_file(
        self,
        db: Session,
        image_id: int,
        user_id: int,
    ) -> dict:
        """
        Generate a temporary presigned URL for previewing
        an original image.
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
            # Preview URL.
            # No Content-Disposition: attachment.
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
        Generate a temporary presigned URL for previewing
        a transformed image.
        """

        logger.info(
            "Getting transformed image preview | "
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
            # Preview URL.
            # IMPORTANT:
            # Do not set download=True here.
            url = storage.download_url(
                storage_key=transformation.storage_key,
                expires=3600,
                download=False,
            )

        except Exception as exc:
            logger.exception(
                "Failed to generate transformed preview URL | "
                "transformation_id=%s | user_id=%s",
                transformation_id,
                user_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transformed image file not found.",
            ) from exc

        logger.info(
            "Transformed image preview URL generated successfully | "
            "transformation_id=%s | user_id=%s",
            transformation_id,
            user_id,
        )

        return {
            "url": url,
            "mime_type": transformation.mime_type,
            "expires_in": 3600,
        }

    
    def get_original_download(
        self,
        db: Session,
        image_id: int,
        user_id: int,
    ) -> dict:

        image = (
            db.query(Image)
            .filter(
                Image.id == image_id,
                Image.user_id == user_id,
            )
            .first()
        )

        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found.",
            )

        filename = image.original_filename or f"image_{image.id}"

        try:
            url = storage.download_url(
                storage_key=image.storage_key,
                expires=3600,
                filename=filename,
                download=True,
            )

        except Exception as exc:
            logger.exception(
                "Failed to generate original download URL | image_id=%s",
                image_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image file not found.",
            ) from exc

        return {
            "url": url,
            "mime_type": image.mime_type,
            "expires_in": 3600,
        }


    def get_transformed_download(
        self,
        db: Session,
        transformation_id: int,
        user_id: int,
    ) -> dict:

        transformation = (
            db.query(ImageTransformation)
            .filter(
                ImageTransformation.id == transformation_id,
                ImageTransformation.user_id == user_id,
            )
            .first()
        )

        if not transformation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transformation not found.",
            )

        filename = (
            f"transformed_{transformation.id}."
            f"{transformation.format.lower()}"
        )

        try:
            url = storage.download_url(
                storage_key=transformation.storage_key,
                expires=3600,
                filename=filename,
                download=True,
            )

        except Exception as exc:
            logger.exception(
                "Failed to generate transformed download URL | "
                "transformation_id=%s",
                transformation_id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transformed image file not found.",
            ) from exc

        return {
            "url": url,
            "mime_type": transformation.mime_type,
            "expires_in": 3600,
        }