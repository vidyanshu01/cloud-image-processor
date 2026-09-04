from pydantic import BaseModel, EmailStr, Field

from app.core.logging import logger


logger.info("Auth schemas loaded")


class UserRegister(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=50,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserLogin(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=50,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):

    id: int

    username: str

    email: EmailStr

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):

    access_token: str

    token_type: str

    user: UserResponse