import io

from fastapi.testclient import TestClient
from PIL import Image


def create_image(
    image_format: str = "PNG",
    size: tuple[int, int] = (100, 100),
) -> io.BytesIO:
    image = Image.new(
        "RGB",
        size,
        color="red",
    )

    file = io.BytesIO()

    image.save(
        file,
        format=image_format,
    )

    file.seek(0)

    return file


def test_upload_png(
    client: TestClient,
    auth_token: str,
):
    image = create_image("PNG")

    response = client.post(
        "/api/v1/images",
        headers={
            "Authorization": f"Bearer {auth_token}",
        },
        files={
            "file": (
                "test.png",
                image,
                "image/png",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["original_filename"] == "test.png"
    assert data["mime_type"] == "image/png"
    assert data["format"] == "PNG"
    assert data["width"] == 100
    assert data["height"] == 100
    assert data["file_size"] > 0


def test_upload_jpeg(
    client: TestClient,
    auth_token: str,
):
    image = create_image("JPEG")

    response = client.post(
        "/api/v1/images",
        headers={
            "Authorization": f"Bearer {auth_token}",
        },
        files={
            "file": (
                "test.jpg",
                image,
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["original_filename"] == "test.jpg"
    assert data["mime_type"] == "image/jpeg"
    assert data["format"] == "JPEG"
    assert data["width"] == 100
    assert data["height"] == 100
    assert data["file_size"] > 0


def test_upload_requires_authentication(
    client: TestClient,
):
    image = create_image("PNG")

    response = client.post(
        "/api/v1/images",
        files={
            "file": (
                "unauthorized.png",
                image,
                "image/png",
            )
        },
    )

    assert response.status_code == 401


def test_upload_invalid_file_type(
    client: TestClient,
    auth_token: str,
):
    text_file = io.BytesIO(
        b"This is not an image."
    )

    response = client.post(
        "/api/v1/images",
        headers={
            "Authorization": f"Bearer {auth_token}",
        },
        files={
            "file": (
                "test.txt",
                text_file,
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_upload_corrupted_image(
    client: TestClient,
    auth_token: str,
):
    corrupted_file = io.BytesIO(
        b"\x89PNG\r\n\x1a\n"
        b"not a valid image"
    )

    response = client.post(
        "/api/v1/images",
        headers={
            "Authorization": f"Bearer {auth_token}",
        },
        files={
            "file": (
                "corrupted.png",
                corrupted_file,
                "image/png",
            )
        },
    )

    assert response.status_code == 400


def test_upload_empty_file(
    client: TestClient,
    auth_token: str,
):
    empty_file = io.BytesIO()

    response = client.post(
        "/api/v1/images",
        headers={
            "Authorization": f"Bearer {auth_token}",
        },
        files={
            "file": (
                "empty.png",
                empty_file,
                "image/png",
            )
        },
    )

    assert response.status_code == 400


def test_upload_image_metadata(
    client: TestClient,
    auth_token: str,
):
    image = create_image(
        image_format="PNG",
        size=(640, 480),
    )

    response = client.post(
        "/api/v1/images",
        headers={
            "Authorization": f"Bearer {auth_token}",
        },
        files={
            "file": (
                "metadata.png",
                image,
                "image/png",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["original_filename"] == "metadata.png"
    assert data["mime_type"] == "image/png"
    assert data["format"] == "PNG"
    assert data["width"] == 640
    assert data["height"] == 480
    assert data["file_size"] > 0