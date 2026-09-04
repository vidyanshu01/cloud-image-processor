from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.logging import logger

from app.models.image import Image
from app.models.user import User

from app.schemas.image import (
    FileAccessResponse,
    ImageListResponse,
    ImageResponse,
)
from app.schemas.image_query import ImageQueryParams
from app.schemas.transformation import (
    TransformationRequest,
    TransformationResponse,
)

from app.services.file_service import ImageFileService
from app.services.image_service import (
    create_image,
    delete_image,
    get_user_images,
)
from app.services.image_validator import validate_file_size
from app.services.transformation_service import process_transformation


logger.info("Image router loaded")


router = APIRouter(
    prefix="/api/v1/images",
    tags=["Images"],
)


file_service = ImageFileService()


@router.post(
    "",
    response_model=ImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload an image for the authenticated user.
    """

    temp_path: str | None = None

    logger.info(
        "Image upload started | user_id=%s | filename=%s",
        current_user.id,
        file.filename,
    )

    try:
        original_filename = file.filename or "image"

        if file.size is None:
            logger.warning(
                "Upload rejected | file size unavailable | user_id=%s",
                current_user.id,
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not determine file size.",
            )

        try:
            validate_file_size(file.size)

        except ValueError as exc:
            logger.warning(
                "Upload rejected | file too large | "
                "user_id=%s | size=%s",
                current_user.id,
                file.size,
            )

            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=str(exc),
            ) from exc


        with NamedTemporaryFile(
            suffix=".upload",
            delete=False,
        ) as temp_file:

            temp_path = temp_file.name

            while chunk := await file.read(1024 * 1024):
                temp_file.write(chunk)

        logger.info(
            "Temporary upload file created | "
            "user_id=%s | path=%s",
            current_user.id,
            temp_path,
        )

        image = create_image(
            db=db,
            user_id=current_user.id,
            file_path=temp_path,
            original_filename=original_filename,
            content_type=file.content_type,
            file_size=file.size,
        )

        logger.info(
            "Image upload completed | "
            "image_id=%s | user_id=%s",
            image.id,
            current_user.id,
        )

        return image

    except HTTPException:
        raise

    except ValueError as exc:
        logger.warning(
            "Image upload validation failed | "
            "user_id=%s | error=%s",
            current_user.id,
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected image upload error | "
            "user_id=%s",
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image.",
        ) from exc

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)

                logger.info(
                    "Temporary upload file removed | "
                    "user_id=%s",
                    current_user.id,
                )

            except Exception:
                logger.exception(
                    "Failed to remove temporary upload file | "
                    "user_id=%s | path=%s",
                    current_user.id,
                    temp_path,
                )

        await file.close()


@router.get(
    "",
    response_model=ImageListResponse,
)
def list_images(
    params: ImageQueryParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return paginated images belonging to the authenticated user.
    """

    logger.info(
        "Image list requested | "
        "user_id=%s | page=%s | limit=%s",
        current_user.id,
        params.page,
        params.limit,
    )

    return get_user_images(
        db=db,
        user_id=current_user.id,
        params=params,
    )


@router.get(
    "/transformations/{transformation_id}/file",
    response_model=FileAccessResponse,
)
def get_transformed_image_file(
    transformation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a temporary S3 presigned URL
    for a transformed image.
    """

    logger.info(
        "Transformed file requested | "
        "transformation_id=%s | user_id=%s",
        transformation_id,
        current_user.id,
    )

    return file_service.get_transformed_file(
        db=db,
        transformation_id=transformation_id,
        user_id=current_user.id,
    )


@router.get(
    "/{image_id}/file",
    response_model=FileAccessResponse,
)
def get_image_file(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a temporary S3 presigned URL
    for viewing the original image.
    """

    logger.info(
        "Image file requested | "
        "image_id=%s | user_id=%s",
        image_id,
        current_user.id,
    )

    return file_service.get_original_file(
        db=db,
        image_id=image_id,
        user_id=current_user.id,
    )


@router.get(
    "/{image_id}/download",
    response_model=FileAccessResponse,
)
def download_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a temporary S3 presigned URL
    for downloading the original image.
    """

    logger.info(
        "Image download requested | "
        "image_id=%s | user_id=%s",
        image_id,
        current_user.id,
    )

    return file_service.get_original_file(
        db=db,
        image_id=image_id,
        user_id=current_user.id,
    )


@router.get(
    "/{image_id}",
    response_model=ImageResponse,
)
def get_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return metadata for a single image.
    """

    logger.info(
        "Image requested | "
        "image_id=%s | user_id=%s",
        image_id,
        current_user.id,
    )

    image = (
        db.query(Image)
        .filter(
            Image.id == image_id,
            Image.user_id == current_user.id,
        )
        .first()
    )

    if not image:
        logger.warning(
            "Image not found | "
            "image_id=%s | user_id=%s",
            image_id,
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found.",
        )

    logger.info(
        "Image metadata retrieved | "
        "image_id=%s | user_id=%s",
        image_id,
        current_user.id,
    )

    return image


@router.post(
    "/{image_id}/transform",
    response_model=TransformationResponse,
    status_code=status.HTTP_201_CREATED,
)
def transform_image(
    image_id: int,
    transformations: TransformationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Apply transformations to an existing image.
    """

    logger.info(
        "Image transformation requested | "
        "image_id=%s | user_id=%s",
        image_id,
        current_user.id,
    )

    image_record = (
        db.query(Image)
        .filter(
            Image.id == image_id,
            Image.user_id == current_user.id,
        )
        .first()
    )

    if not image_record:
        logger.warning(
            "Transformation rejected | image not found | "
            "image_id=%s | user_id=%s",
            image_id,
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found.",
        )

    try:
        result, cached = process_transformation(
            db=db,
            image_record=image_record,
            user_id=current_user.id,
            transformations=transformations,
        )

    except ValueError as exc:
        logger.warning(
            "Transformation validation failed | "
            "image_id=%s | user_id=%s | error=%s",
            image_id,
            current_user.id,
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Transformation failed | "
            "image_id=%s | user_id=%s",
            image_id,
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transform image.",
        ) from exc

    logger.info(
        "Transformation completed | "
        "image_id=%s | transformation_id=%s | cached=%s",
        image_id,
        result.id,
        cached,
    )

    return {
        "id": result.id,
        "image_id": result.image_id,
        "storage_key": result.storage_key,
        "format": result.format,
        "mime_type": result.mime_type,
        "width": result.width,
        "height": result.height,
        "file_size": result.file_size,
        "cached": cached,
        "created_at": result.created_at,
    }


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_image_endpoint(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete an image and its transformed versions.
    """

    logger.info(
        "Image deletion requested | "
        "image_id=%s | user_id=%s",
        image_id,
        current_user.id,
    )

    try:
        delete_image(
            db=db,
            image_id=image_id,
            user_id=current_user.id,
        )

    except ValueError as exc:


        if str(exc) == "Image not found.":

            logger.warning(
                "Image deletion failed | image not found | "
                "image_id=%s | user_id=%s",
                image_id,
                current_user.id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found.",
            ) from exc

        logger.exception(
            "Image deletion failed | "
            "image_id=%s | user_id=%s",
            image_id,
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete image.",
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected image deletion error | "
            "image_id=%s | user_id=%s",
            image_id,
            current_user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete image.",
        ) from exc

    logger.info(
        "Image deleted successfully | "
        "image_id=%s | user_id=%s",
        image_id,
        current_user.id,
    )

    return None