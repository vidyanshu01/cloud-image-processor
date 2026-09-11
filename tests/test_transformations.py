import io
import uuid

from PIL import Image as PILImage


def create_test_image(
    filename: str = "transform_test.png",
    image_format: str = "PNG",
    size: tuple[int, int] = (400, 300),
):
    image = PILImage.new("RGB", size, "red")

    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    buffer.seek(0)

    return filename, buffer, f"image/{image_format.lower()}"


def upload_test_image(client, token: str):
    filename, image_file, content_type = create_test_image()

    response = client.post(
        "/api/v1/images",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                filename,
                image_file,
                content_type,
            )
        },
    )

    assert response.status_code == 201, response.text

    return response.json()


def transform_image(
    client,
    token: str,
    image_id: int,
    payload: dict,
):
    return client.post(
        f"/api/v1/images/{image_id}/transform",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )


def test_resize(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "resize": {
                "width": 200,
                "height": 150,
            }
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["image_id"] == image["id"]
    assert data["width"] == 200
    assert data["height"] == 150
    assert data["format"]
    assert data["mime_type"]
    assert data["file_size"] > 0
    assert "storage_key" in data
    assert data["cached"] is False


def test_crop(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "crop": {
                "width": 200,
                "height": 100,
                "x": 20,
                "y": 20,
            }
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["image_id"] == image["id"]
    assert data["width"] == 200
    assert data["height"] == 100
    assert data["file_size"] > 0


def test_rotate(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "rotate": 90,
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["image_id"] == image["id"]
    assert data["width"] > 0
    assert data["height"] > 0
    assert data["file_size"] > 0


def test_flip(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "flip": True,
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["image_id"] == image["id"]
    assert data["width"] == 400
    assert data["height"] == 300
    assert data["file_size"] > 0


def test_mirror(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "mirror": True,
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["image_id"] == image["id"]
    assert data["width"] == 400
    assert data["height"] == 300
    assert data["file_size"] > 0


def test_grayscale(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "filter": {
                "grayscale": True,
            }
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["image_id"] == image["id"]
    assert data["file_size"] > 0


def test_sepia(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "filter": {
                "sepia": True,
            }
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["image_id"] == image["id"]
    assert data["file_size"] > 0


def test_format_conversion_to_jpeg(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "format": "JPEG",
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["image_id"] == image["id"]
    assert data["format"] == "JPEG"
    assert data["mime_type"] == "image/jpeg"
    assert data["file_size"] > 0


def test_format_conversion_to_webp(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "format": "WEBP",
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["image_id"] == image["id"]
    assert data["format"] == "WEBP"
    assert data["mime_type"] == "image/webp"
    assert data["file_size"] > 0


def test_quality_parameter(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "format": "JPEG",
            "quality": 50,
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["image_id"] == image["id"]
    assert data["format"] == "JPEG"
    assert data["file_size"] > 0


def test_combined_transformations(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "resize": {
                "width": 200,
                "height": 150,
            },
            "rotate": 90,
            "flip": True,
            "filter": {
                "grayscale": True,
            },
            "format": "JPEG",
            "quality": 80,
        },
    )

    assert response.status_code == 201, response.text

    data = response.json()

    assert data["image_id"] == image["id"]
    assert data["format"] == "JPEG"
    assert data["mime_type"] == "image/jpeg"
    assert data["width"] > 0
    assert data["height"] > 0
    assert data["file_size"] > 0


def test_transformation_cache_miss_then_hit(client, auth_token):
    image = upload_test_image(client, auth_token)

    payload = {
        "resize": {
            "width": 200,
            "height": 150,
        }
    }

    first_response = transform_image(
        client,
        auth_token,
        image["id"],
        payload,
    )

    assert first_response.status_code == 201, first_response.text

    first_data = first_response.json()

    assert first_data["cached"] is False

    second_response = transform_image(
        client,
        auth_token,
        image["id"],
        payload,
    )

    assert second_response.status_code == 201, second_response.text

    second_data = second_response.json()

    assert second_data["cached"] is True
    assert second_data["id"] == first_data["id"]
    assert second_data["storage_key"] == first_data["storage_key"]


def test_different_transformations_create_different_results(
    client,
    auth_token,
):
    image = upload_test_image(client, auth_token)

    resize_response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "resize": {
                "width": 200,
                "height": 150,
            }
        },
    )

    assert resize_response.status_code == 201

    grayscale_response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "filter": {
                "grayscale": True,
            }
        },
    )

    assert grayscale_response.status_code == 201

    resize_data = resize_response.json()
    grayscale_data = grayscale_response.json()

    assert resize_data["id"] != grayscale_data["id"]
    assert resize_data["storage_key"] != grayscale_data["storage_key"]


def test_transform_nonexistent_image(client, auth_token):
    response = transform_image(
        client,
        auth_token,
        999999999,
        {
            "resize": {
                "width": 200,
                "height": 150,
            }
        },
    )

    assert response.status_code == 404


def test_transform_requires_authentication(client):
    response = client.post(
        "/api/v1/images/1/transform",
        json={
            "resize": {
                "width": 200,
                "height": 150,
            }
        },
    )

    assert response.status_code in (401, 403)


def test_invalid_resize_width(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "resize": {
                "width": 0,
                "height": 150,
            }
        },
    )

    assert response.status_code == 422


def test_invalid_resize_height(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "resize": {
                "width": 200,
                "height": 0,
            }
        },
    )

    assert response.status_code == 422


def test_invalid_crop_coordinates(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "crop": {
                "width": 100,
                "height": 100,
                "x": -1,
                "y": 0,
            }
        },
    )

    assert response.status_code == 422


def test_invalid_rotation(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "rotate": 361,
        },
    )

    assert response.status_code == 422


def test_invalid_quality(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "quality": 101,
        },
    )

    assert response.status_code == 422


def test_invalid_format(client, auth_token):
    image = upload_test_image(client, auth_token)

    response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "format": "BMP",
        },
    )

    assert response.status_code == 422


def test_transformed_file_url(client, auth_token):
    image = upload_test_image(client, auth_token)

    transform_response = transform_image(
        client,
        auth_token,
        image["id"],
        {
            "resize": {
                "width": 200,
                "height": 150,
            }
        },
    )

    assert transform_response.status_code == 201, (
        transform_response.text
    )

    transformation_id = transform_response.json()["id"]

    response = client.get(
        f"/api/v1/images/transformations/"
        f"{transformation_id}/file",
        headers={
            "Authorization": f"Bearer {auth_token}",
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "url" in data
    assert data["url"]


def test_second_user_cannot_transform_first_users_image(
    client,
    auth_token,
):
    image = upload_test_image(client, auth_token)

    unique_id = uuid.uuid4().hex[:8]

    second_user = {
        "username": f"transform_user_{unique_id}",
        "email": f"transform_user_{unique_id}@example.com",
        "password": "TestPassword123!",
    }

    register_response = client.post(
        "/api/v1/auth/register",
        json=second_user,
    )

    assert register_response.status_code == 201, (
        register_response.text
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": second_user["username"],
            "password": second_user["password"],
        },
    )

    assert login_response.status_code == 200, login_response.text

    second_token = login_response.json()["access_token"]

    response = transform_image(
        client,
        second_token,
        image["id"],
        {
            "resize": {
                "width": 200,
                "height": 150,
            }
        },
    )

    assert response.status_code == 404