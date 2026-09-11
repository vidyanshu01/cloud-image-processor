import io
import os
import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


# ---------------------------------------------------------
# Test database
# ---------------------------------------------------------

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite://",
)

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
    if TEST_DATABASE_URL.startswith("sqlite")
    else {},
    poolclass=StaticPool
    if TEST_DATABASE_URL.startswith("sqlite")
    else None,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create the test database schema for the test session."""
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Provide a clean database session for each test."""
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ---------------------------------------------------------
# Fake object storage
# ---------------------------------------------------------

class FakeStorage:
    """
    In-memory object storage used by API tests.

    This prevents tests from contacting Backblaze B2/S3.
    Real storage behavior is tested separately in
    tests/test_storage.py using the integration marker.
    """

    def __init__(self):
        self.objects: dict[str, bytes] = {}

    def upload_file(
        self,
        file_path: str,
        storage_key: str,
        content_type: str | None = None,
    ) -> None:
        with open(file_path, "rb") as file:
            self.objects[storage_key] = file.read()

    def upload_bytes(
        self,
        data: bytes,
        storage_key: str,
        content_type: str | None = None,
    ) -> None:
        self.objects[storage_key] = data

    def download(
        self,
        storage_key: str,
    ) -> bytes | None:
        return self.objects.get(storage_key)

    def delete(
        self,
        storage_key: str,
    ) -> None:
        self.objects.pop(storage_key, None)

    def download_url(
        self,
        storage_key: str,
        expires: int = 3600,
    ) -> str:
        if storage_key not in self.objects:
            raise FileNotFoundError(storage_key)

        return (
            f"http://fake-storage.local/"
            f"{storage_key}?expires={expires}"
        )


@pytest.fixture
def fake_storage(monkeypatch) -> FakeStorage:
    """
    Replace application storage with in-memory storage.

    The application imports the shared storage object directly
    inside these service modules, so each imported reference is
    patched explicitly.
    """

    fake = FakeStorage()

    import app.services.file_service as file_service_module
    import app.services.image_service as image_service_module
    import app.services.transformation_service as transformation_module

    monkeypatch.setattr(
        image_service_module,
        "storage",
        fake,
    )

    monkeypatch.setattr(
        file_service_module,
        "storage",
        fake,
    )

    monkeypatch.setattr(
        transformation_module,
        "storage",
        fake,
    )

    return fake


# ---------------------------------------------------------
# FastAPI database override
# ---------------------------------------------------------

@pytest.fixture
def client(
    db: Session,
    fake_storage: FakeStorage,
) -> Generator[TestClient, None, None]:
    """Create a FastAPI test client using test DB and fake storage."""

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ---------------------------------------------------------
# Test user data
# ---------------------------------------------------------

@pytest.fixture
def user_data() -> dict:
    unique_id = uuid.uuid4().hex[:8]

    return {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "TestPassword123!",
    }


@pytest.fixture
def second_user_data() -> dict:
    """Return valid data for a second test user."""

    unique_id = uuid.uuid4().hex[:8]

    return {
        "username": f"seconduser_{unique_id}",
        "email": f"seconduser_{unique_id}@example.com",
        "password": "SecondPassword123!",
    }


# ---------------------------------------------------------
# Authentication fixtures
# ---------------------------------------------------------

@pytest.fixture
def registered_user(
    client: TestClient,
    user_data: dict,
) -> dict:
    """Register and return a test user."""

    response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    assert response.status_code == 201

    return response.json()


@pytest.fixture
def auth_token(
    client: TestClient,
    user_data: dict,
) -> str:
    """Register a user and return its JWT access token."""

    register_response = client.post(
        "/api/v1/auth/register",
        json=user_data,
    )

    assert register_response.status_code == 201, (
        f"Registration failed: "
        f"{register_response.status_code} "
        f"{register_response.text}"
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == 200, (
        f"Login failed: "
        f"{login_response.status_code} "
        f"{login_response.text}"
    )

    data = login_response.json()

    assert "access_token" in data

    return data["access_token"]


@pytest.fixture
def auth_headers(
    auth_token: str,
) -> dict:
    """Return Bearer authentication headers."""

    return {
        "Authorization": f"Bearer {auth_token}",
    }


# ---------------------------------------------------------
# Image fixtures
# ---------------------------------------------------------

@pytest.fixture
def test_image() -> tuple[str, tuple[str, io.BytesIO, str]]:
    """Create an in-memory PNG image for upload tests."""

    from PIL import Image

    image = Image.new(
        "RGB",
        (100, 100),
        color="white",
    )

    image_bytes = io.BytesIO()

    image.save(
        image_bytes,
        format="PNG",
    )

    image_bytes.seek(0)

    return (
        "test.png",
        (
            "test.png",
            image_bytes,
            "image/png",
        ),
    )


@pytest.fixture
def test_jpeg_image() -> tuple[str, tuple[str, io.BytesIO, str]]:
    """Create an in-memory JPEG image for upload tests."""

    from PIL import Image

    image = Image.new(
        "RGB",
        (100, 100),
        color="white",
    )

    image_bytes = io.BytesIO()

    image.save(
        image_bytes,
        format="JPEG",
    )

    image_bytes.seek(0)

    return (
        "test.jpg",
        (
            "test.jpg",
            image_bytes,
            "image/jpeg",
        ),
    )


# ---------------------------------------------------------
# Authorization helper
# ---------------------------------------------------------

@pytest.fixture
def second_auth_token(
    client: TestClient,
    second_user_data: dict,
) -> str:
    """Register a second user and return its JWT."""

    register_response = client.post(
        "/api/v1/auth/register",
        json=second_user_data,
    )

    assert register_response.status_code == 201, (
        register_response.text
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": second_user_data["username"],
            "password": second_user_data["password"],
        },
    )

    assert login_response.status_code == 200, (
        login_response.text
    )

    return login_response.json()["access_token"]


@pytest.fixture
def second_auth_headers(
    second_auth_token: str,
) -> dict:
    """Return Bearer headers for the second user."""

    return {
        "Authorization": f"Bearer {second_auth_token}",
    }