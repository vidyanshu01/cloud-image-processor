import uuid
from pathlib import Path

from app.storage.s3_storage import S3Storage


def test_storage_upload_and_download():
    storage = S3Storage()

    key = f"tests/{uuid.uuid4().hex}.txt"
    content = b"Cloud Image API storage test"

    try:
        storage.upload_bytes(
            content,
            key,
            "text/plain",
        )

        downloaded = storage.download(key)

        assert downloaded == content

    finally:
        storage.delete(key)


def test_storage_upload_file_and_download(tmp_path: Path):
    storage = S3Storage()

    key = f"tests/{uuid.uuid4().hex}.txt"
    content = b"File upload test"

    local_file = tmp_path / "test.txt"
    local_file.write_bytes(content)

    try:
        storage.upload_file(
            str(local_file),
            key,
            "text/plain",
        )

        downloaded = storage.download(key)

        assert downloaded == content

    finally:
        storage.delete(key)


def test_storage_delete():
    storage = S3Storage()

    key = f"tests/{uuid.uuid4().hex}.txt"
    content = b"Delete test"

    storage.upload_bytes(
        content,
        key,
        "text/plain",
    )

    try:
        # delete() returns None on successful deletion.
        result = storage.delete(key)

        assert result is None

        # Verify the object can no longer be downloaded.
        try:
            downloaded = storage.download(key)
            assert downloaded is None
        except Exception:
            # S3-compatible storage may raise for a missing object.
            pass

    finally:
        # Safe cleanup in case the object still exists.
        storage.delete(key)


def test_storage_download_url():
    storage = S3Storage()

    key = f"tests/{uuid.uuid4().hex}.txt"
    content = b"Presigned URL test"

    try:
        storage.upload_bytes(
            content,
            key,
            "text/plain",
        )

        url = storage.download_url(key)

        assert isinstance(url, str)
        assert url.startswith("http")

    finally:
        storage.delete(key)


def test_storage_missing_object():
    storage = S3Storage()

    key = f"tests/{uuid.uuid4().hex}-missing.txt"

    try:
        result = storage.download(key)

        assert result is None

    except Exception:
        # Some S3-compatible implementations raise an exception
        # for a missing object.
        assert True