import io

from PIL import Image


def create_test_image():
    image = Image.new("RGB", (300, 200), "blue")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def upload_image(client, token):
    image = create_test_image()

    response = client.post(
        "/api/v1/images",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                "file_service_test.png",
                image,
                "image/png",
            )
        },
    )

    assert response.status_code == 201, response.text

    return response.json()


def transform_image(client, token, image_id):
    response = client.post(
        f"/api/v1/images/{image_id}/transform",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "resize": {
                "width": 150,
                "height": 100,
            }
        },
    )

    assert response.status_code == 201, response.text

    return response.json()


def test_original_file_url(client, auth_token):
    image = upload_image(client, auth_token)

    response = client.get(
        f"/api/v1/images/{image['id']}/file",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "url" in data
    assert isinstance(data["url"], str)
    assert data["url"].startswith("http")


def test_original_download_url(client, auth_token):
    image = upload_image(client, auth_token)

    response = client.get(
        f"/api/v1/images/{image['id']}/download",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "url" in data
    assert isinstance(data["url"], str)
    assert data["url"].startswith("http")


def test_transformed_file_url(client, auth_token):
    image = upload_image(client, auth_token)

    transformation = transform_image(
        client,
        auth_token,
        image["id"],
    )

    transformation_id = transformation["id"]

    response = client.get(
        f"/api/v1/images/transformations/{transformation_id}/file",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "url" in data
    assert isinstance(data["url"], str)
    assert data["url"].startswith("http")


def test_file_url_requires_authentication(client, auth_token):
    image = upload_image(client, auth_token)

    response = client.get(
        f"/api/v1/images/{image['id']}/file"
    )

    assert response.status_code in (401, 403)


def test_download_url_requires_authentication(client, auth_token):
    image = upload_image(client, auth_token)

    response = client.get(
        f"/api/v1/images/{image['id']}/download"
    )

    assert response.status_code in (401, 403)


def test_nonexistent_image_file(client, auth_token):
    response = client.get(
        "/api/v1/images/999999/file",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 404


def test_nonexistent_image_download(client, auth_token):
    response = client.get(
        "/api/v1/images/999999/download",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 404


def test_nonexistent_transformation_file(client, auth_token):
    response = client.get(
        "/api/v1/images/transformations/999999/file",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 404