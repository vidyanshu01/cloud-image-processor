from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logging import logger
from app.core.security import decode_access_token
from app.models.user import User


logger.info("Dependencies module loaded")


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Authenticate the request using a JWT access token
    and return the corresponding user.
    """

    logger.info("Authentication request started")

    token = credentials.credentials

    payload = decode_access_token(token)

    if not payload:

        logger.warning(
            "Invalid or expired JWT token",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


    user_id = payload.get("sub")

    if not user_id:

        logger.warning(
            "JWT token missing user ID",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    try:

        user_id = int(user_id)

    except (ValueError, TypeError) as exc:

        logger.warning(
            "Invalid user ID in JWT",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc

    user = (
        db.query(User)
        .filter(
            User.id == user_id,
        )
        .first()
    )

    if not user:

        logger.warning(
            "Authenticated user not found | user_id=%s",
            user_id,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    logger.info(
        "Authentication successful | user_id=%s",
        user.id,
    )

    return user