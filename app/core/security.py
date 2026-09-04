from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.logging import logger


logger.info("Security module loaded")


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using Argon2.
    """

    logger.info("Password hashing started")

    hashed_password = pwd_context.hash(password)

    logger.info("Password hashing completed")

    return hashed_password

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against its Argon2 hash.
    """

    logger.info("Password verification started")

    try:

        result = pwd_context.verify(
            plain_password,
            hashed_password,
        )

    except Exception:

        logger.exception(
            "Password verification failed",
        )

        return False

    logger.info(
        "Password verification completed | valid=%s",
        result,
    )

    return result

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.
    """

    logger.info("JWT creation started")

    to_encode = data.copy()

    if expires_delta:

        expire = (
            datetime.now(timezone.utc)
            + expires_delta
        )

    else:

        expire = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            )
        )

    to_encode.update(
        {
            "exp": expire,
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    logger.info(
        "JWT creation completed | expires_at=%s",
        expire.isoformat(),
    )

    return encoded_jwt

def decode_access_token(
    token: str,
) -> dict | None:
    """
    Decode and verify a JWT access token.

    Returns the decoded payload if valid,
    otherwise returns None.
    """

    logger.info("JWT verification started")

    try:

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[
                settings.JWT_ALGORITHM,
            ],
        )

        logger.info(
            "JWT verification successful",
        )

        return payload

    except JWTError:

        logger.warning(
            "JWT verification failed",
        )

        return None