from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.logging import logger
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)


logger.info("Auth router loaded")


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)




@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Return the currently authenticated user.
    """

    logger.info(
        "Current user requested | user_id=%s",
        current_user.id,
    )

    return current_user



@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    """
    Register a new user and return an access token.
    """

    logger.info(
        "Registration attempt | username=%s",
        user_data.username,
    )


    existing_user = (
        db.query(User)
        .filter(
            User.username == user_data.username,
        )
        .first()
    )

    if existing_user:

        logger.warning(
            "Registration failed | username already exists",
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )



    existing_email = (
        db.query(User)
        .filter(
            User.email == user_data.email,
        )
        .first()
    )

    if existing_email:

        logger.warning(
            "Registration failed | email already exists",
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )


    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(
            user_data.password,
        ),
    )

    try:

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except Exception as exc:

        db.rollback()

        logger.exception(
            "User registration failed | username=%s",
            user_data.username,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create user",
        ) from exc

    # --------------------------------------------------------
    # Create JWT
    # --------------------------------------------------------

    access_token = create_access_token(
        data={
            "sub": str(new_user.id),
        }
    )

    logger.info(
        "User registered successfully | user_id=%s",
        new_user.id,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user,
    }

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Authenticate a user and return an access token.
    """

    logger.info(
        "Login attempt | username=%s",
        user_data.username,
    )

    user = (
        db.query(User)
        .filter(
            User.username == user_data.username,
        )
        .first()
    )


    if not user:

        logger.warning(
            "Login failed | invalid credentials",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not verify_password(
        user_data.password,
        user.password_hash,
    ):

        logger.warning(
            "Login failed | invalid credentials | user_id=%s",
            user.id,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )


    access_token = create_access_token(
        data={
            "sub": str(user.id),
        }
    )

    logger.info(
        "Login successful | user_id=%s",
        user.id,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }