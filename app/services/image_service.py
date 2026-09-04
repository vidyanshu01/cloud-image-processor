from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.image import Image
from app.schemas.image_query import ImageQueryParams
from app.services.image_validator import validate_uploaded_image
from app.storage import storage
from app.utils.storage_key import generate_storage_key


logger.info("Image service loaded")


FORMAT_TO_EXTENSION = {
    "JPEG": "jpg",
    "PNG": "png",
    "WEBP": "webp",
    "GIF": "gif",
}


FORMAT_TO_MIME_TYPE = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
    "GIF": "image/gif",
}


def create_image(
    db: Session,
    user_id: int,
    file_path: str,
    original_filename: str,
    content_type: str | None,
    file_size: int,
) -> Image:
    """Validate, upload, and persist an image."""

    logger.info(
        "Image creation started | user_id=%s | filename=%s",
        user_id,
        original_filename,
    )


    logger.info(
        "Validating uploaded image | filename=%s",
        original_filename,
    )

    metadata = validate_uploaded_image(
        file_path=file_path,
        file_size=file_size,
        content_type=content_type,
    )

    image_format = metadata["format"].upper()

    extension = FORMAT_TO_EXTENSION.get(image_format)

    if extension is None:
        logger.warning(
            "Unsupported image format | format=%s",
            image_format,
        )
        raise ValueError("Unsupported image format.")

    final_mime_type = FORMAT_TO_MIME_TYPE.get(image_format)

    if final_mime_type is None:
        logger.warning(
            "Unable to determine MIME type | format=%s",
            image_format,
        )
        raise ValueError("Unsupported image format.")

    logger.info(
        "Image metadata detected | format=%s | mime_type=%s | "
        "width=%s | height=%s",
        image_format,
        final_mime_type,
        metadata["width"],
        metadata["height"],
    )

    storage_key = generate_storage_key(
        user_id=user_id,
        extension=extension,
    )

    logger.info(
        "S3 storage key generated | key=%s",
        storage_key,
    )

    try:
        logger.info(
            "Uploading image to S3 | key=%s",
            storage_key,
        )

        storage.upload_file(
            file_path=file_path,
            storage_key=storage_key,
            content_type=final_mime_type,
        )

    except Exception as exc:
        logger.exception(
            "S3 upload failed | key=%s",
            storage_key,
        )

        raise ValueError(
            "Failed to upload image."
        ) from exc

    image = Image(
        user_id=user_id,
        original_filename=original_filename,
        storage_key=storage_key,
        mime_type=final_mime_type,
        format=image_format,
        width=metadata["width"],
        height=metadata["height"],
        file_size=file_size,
    )

    try:
        logger.info(
            "Saving image metadata to database | key=%s",
            storage_key,
        )

        db.add(image)
        db.commit()
        db.refresh(image)

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Database save failed | key=%s",
            storage_key,
        )

        try:
            storage.delete(storage_key)

            logger.info(
                "S3 cleanup successful | key=%s",
                storage_key,
            )

        except Exception:
            logger.exception(
                "S3 cleanup failed | key=%s",
                storage_key,
            )

        raise

    logger.info(
        "Image creation completed | image_id=%s | user_id=%s",
        image.id,
        user_id,
    )

    return image


def get_user_images(
    db: Session,
    user_id: int,
    params: ImageQueryParams,
) -> dict:
    """Return paginated images belonging to a user."""

    logger.info(
        "Finding user images | user_id=%s | page=%s | limit=%s",
        user_id,
        params.page,
        params.limit,
    )

    query = db.query(Image).filter(
        Image.user_id == user_id
    )

    if params.search:
        logger.info(
            "Applying image search | user_id=%s | search=%s",
            user_id,
            params.search,
        )

        search_term = f"%{params.search}%"

        query = query.filter(
            Image.original_filename.ilike(search_term)
        )

    if params.format:
        normalized_format = params.format.upper()

        logger.info(
            "Applying format filter | user_id=%s | format=%s",
            user_id,
            normalized_format,
        )

        query = query.filter(
            Image.format == normalized_format
        )
        
    if params.sort == "newest":
        query = query.order_by(
            desc(Image.created_at),
            desc(Image.id),
        )

    elif params.sort == "oldest":
        query = query.order_by(
            asc(Image.created_at),
            asc(Image.id),
        )

    elif params.sort == "largest":
        query = query.order_by(
            desc(Image.file_size),
            desc(Image.id),
        )

    elif params.sort == "smallest":
        query = query.order_by(
            asc(Image.file_size),
            asc(Image.id),
        )

    total = query.count()

    offset = (params.page - 1) * params.limit

    images = (
        query
        .offset(offset)
        .limit(params.limit)
        .all()
    )

    total_pages = (
        total + params.limit - 1
    ) // params.limit

    logger.info(
        "Images found | user_id=%s | total=%s | page=%s",
        user_id,
        total,
        params.page,
    )

    return {
        "page": params.page,
        "limit": params.limit,
        "total": total,
        "total_pages": total_pages,
        "items": images,
    }


def delete_image(
    db: Session,
    image_id: int,
    user_id: int,
) -> None:
    """Delete an image and all associated transformed files."""

    logger.info(
        "Image deletion started | image_id=%s | user_id=%s",
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
            "Image not found | image_id=%s | user_id=%s",
            image_id,
            user_id,
        )

        raise ValueError("Image not found.")

    transformation_cleanup_failed = False

    for transformation in image.transformations:
        try:
            logger.info(
                "Deleting transformation from S3 | "
                "transformation_id=%s | key=%s",
                transformation.id,
                transformation.storage_key,
            )

            storage.delete(
                transformation.storage_key
            )

        except Exception:
            transformation_cleanup_failed = True

            logger.exception(
                "Failed to delete transformation from S3 | "
                "transformation_id=%s | key=%s",
                transformation.id,
                transformation.storage_key,
            )

    if transformation_cleanup_failed:
        logger.error(
            "One or more transformation files could not be deleted | "
            "image_id=%s",
            image_id,
        )

        raise ValueError(
            "Failed to completely delete transformed images."
        )
    try:
        logger.info(
            "Deleting original image from S3 | key=%s",
            image.storage_key,
        )

        storage.delete(
            image.storage_key
        )

    except Exception as exc:
        logger.exception(
            "Failed to delete original image from S3 | key=%s",
            image.storage_key,
        )

        raise ValueError(
            "Failed to delete image from storage."
        ) from exc

    try:
        logger.info(
            "Deleting image database record | image_id=%s",
            image_id,
        )

        db.delete(image)
        db.commit()

    except Exception:
        db.rollback()

        logger.exception(
            "Failed to delete image database record | image_id=%s",
            image_id,
        )
        raise

    logger.info(
        "Image deletion completed | image_id=%s | user_id=%s",
        image_id,
        user_id,
    )