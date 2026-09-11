import io

from PIL import Image as PILImage


def create_test_image(
    filename: str = "management_test.png",
    image_format: str = "PNG",
    size: tuple[int, int] = (100, 80),
) -> tuple[str, io.BytesIO, str]:
    image = PILImage.new("RGB", size, "red")

    buffer = io.BytesIO()
    image.save(buffer, format=image_format)
    buffer.seek(0)

    return filename, buffer, f"image/{image_format.lower()}"


def upload_image(client, token: str, filename: str = "management_test.png"):
    actual_filename, image_file, content_type = create_test_image(filename)

    response = client.post(
        "/api/v1/images",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                actual_filename,
                image_file,
                content_type,
            )
        },
    )

    return response


def test_list_images(client, auth_token):
    upload_response = upload_image(
        client,
        auth_token,
        "list_test.png",
    )

    assert upload_response.status_code == 201, upload_response.text

    response = client.get(
        "/api/v1/images",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert isinstance(data, dict)

    # Current API uses paginated image results.
    assert "items" in data
    assert isinstance(data["items"], list)

    assert any(
        item["original_filename"] == "list_test.png"
        for item in data["items"]
    )


def test_list_images_requires_authentication(client):
    response = client.get("/api/v1/images")

    assert response.status_code in (401, 403)


def test_get_image_metadata(client, auth_token):
    upload_response = upload_image(
        client,
        auth_token,
        "metadata_test.png",
    )

    assert upload_response.status_code == 201, upload_response.text

    image_data = upload_response.json()
    image_id = image_data["id"]

    response = client.get(
        f"/api/v1/images/{image_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["id"] == image_id
    assert data["original_filename"] == "metadata_test.png"
    assert data["mime_type"] == "image/png"
    assert data["format"] == "PNG"
    assert data["width"] == 100
    assert data["height"] == 80
    assert data["file_size"] > 0


def test_get_nonexistent_image(client, auth_token):
    response = client.get(
        "/api/v1/images/999999999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 404


def test_search_images(client, auth_token):
    upload_response = upload_image(
        client,
        auth_token,
        "unique_search_image.png",
    )

    assert upload_response.status_code == 201, upload_response.text

    response = client.get(
        "/api/v1/images",
        params={"search": "unique_search"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "items" in data

    assert any(
        item["original_filename"] == "unique_search_image.png"
        for item in data["items"]
    )


def test_filter_images_by_format(client, auth_token):
    upload_response = upload_image(
        client,
        auth_token,
        "format_filter_test.png",
    )

    assert upload_response.status_code == 201, upload_response.text

    response = client.get(
        "/api/v1/images",
        params={"format": "PNG"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "items" in data

    for item in data["items"]:
        assert item["format"].upper() == "PNG"


def test_sort_images(client, auth_token):
    upload_image(
        client,
        auth_token,
        "sort_first.png",
    )

    upload_image(
        client,
        auth_token,
        "sort_second.png",
    )

    response = client.get(
        "/api/v1/images",
        params={
            "sort_by": "created_at",
            "sort_order": "desc",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "items" in data
    assert len(data["items"]) >= 2

    created_dates = [
        item["created_at"]
        for item in data["items"]
    ]

    assert created_dates == sorted(
        created_dates,
        reverse=True,
    )


def test_pagination(client, auth_token):
    upload_image(
        client,
        auth_token,
        "page_one.png",
    )

    upload_image(
        client,
        auth_token,
        "page_two.png",
    )

    response = client.get(
        "/api/v1/images",
        params={
            "page": 1,
            "limit": 1,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "items" in data
    assert len(data["items"]) <= 1


def test_get_file_url(client, auth_token):
    upload_response = upload_image(
        client,
        auth_token,
        "file_url_test.png",
    )

    assert upload_response.status_code == 201, upload_response.text

    image_id = upload_response.json()["id"]

    response = client.get(
        f"/api/v1/images/{image_id}/file",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert isinstance(data, dict)
    assert "url" in data
    assert data["url"]


def test_delete_image(client, auth_token):
    upload_response = upload_image(
        client,
        auth_token,
        "delete_test.png",
    )

    assert upload_response.status_code == 201, upload_response.text

    image_id = upload_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/images/{image_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert delete_response.status_code in (200, 204)

    get_response = client.get(
        f"/api/v1/images/{image_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert get_response.status_code == 404


def test_delete_nonexistent_image(client, auth_token):
    response = client.delete(
        "/api/v1/images/999999999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 404


def test_user_cannot_access_another_users_image(
    client,
    auth_token,
):
    upload_response = upload_image(
        client,
        auth_token,
        "private_image.png",
    )

    assert upload_response.status_code == 201, upload_response.text

    image_id = upload_response.json()["id"]

    # Create a second user.
    import uuid

    unique_id = uuid.uuid4().hex[:8]

    second_user = {
        "username": f"second_user_{unique_id}",
        "email": f"second_user_{unique_id}@example.com",
        "password": "TestPassword123!",
    }

    register_response = client.post(
        "/api/v1/auth/register",
        json=second_user,
    )

    assert register_response.status_code == 201, register_response.text

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": second_user["username"],
            "password": second_user["password"],
        },
    )

    assert login_response.status_code == 200, login_response.text

    second_token = login_response.json()["access_token"]

    response = client.get(
        f"/api/v1/images/{image_id}",
        headers={
            "Authorization": f"Bearer {second_token}",
        },
    )

    assert response.status_code in (403, 404)