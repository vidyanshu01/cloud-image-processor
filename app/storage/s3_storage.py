import io

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.logging import logger


class S3Storage:

    def __init__(self):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL
        )

        self.bucket = settings.AWS_S3_BUCKET_NAME

        logger.info(
            "AWS S3 storage initialized | bucket=%s | region=%s",
            self.bucket,
            settings.AWS_REGION,
        )

    def upload_file(
        self,
        file_path: str,
        storage_key: str,
        content_type: str,
    ) -> None:

        logger.info(
            "S3 upload started | key=%s",
            storage_key,
        )

        try:
            self.client.upload_file(
                file_path,
                self.bucket,
                storage_key,
                ExtraArgs={
                    "ContentType": content_type,
                },
            )

        except ClientError:
            logger.exception(
                "S3 upload failed | key=%s",
                storage_key,
            )
            raise

        logger.info(
            "S3 upload completed | key=%s",
            storage_key,
        )

    def upload_bytes(
        self,
        data: bytes,
        storage_key: str,
        content_type: str,
    ) -> None:

        logger.info(
            "S3 bytes upload started | key=%s | size=%s",
            storage_key,
            len(data),
        )

        try:
            self.client.upload_fileobj(
                io.BytesIO(data),
                self.bucket,
                storage_key,
                ExtraArgs={
                    "ContentType": content_type,
                },
            )

        except ClientError:
            logger.exception(
                "S3 bytes upload failed | key=%s",
                storage_key,
            )
            raise

        logger.info(
            "S3 bytes upload completed | key=%s",
            storage_key,
        )

    def download(
        self,
        storage_key: str,
    ) -> bytes:

        logger.info(
            "S3 download started | key=%s",
            storage_key,
        )

        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=storage_key,
            )

            data = response["Body"].read()

        except ClientError:
            logger.exception(
                "S3 download failed | key=%s",
                storage_key,
            )
            raise

        logger.info(
            "S3 download completed | key=%s | size=%s",
            storage_key,
            len(data),
        )

        return data

    def delete(
        self,
        storage_key: str,
    ) -> None:

        logger.info(
            "S3 delete started | key=%s",
            storage_key,
        )

        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=storage_key,
            )

        except ClientError:
            logger.exception(
                "S3 delete failed | key=%s",
                storage_key,
            )
            raise

        logger.info(
            "S3 delete completed | key=%s",
            storage_key,
        )

    def download_url(
        self,
        storage_key: str,
        expires: int = 3600,
        filename: str | None = None,
        download: bool = False,
    ) -> str:

        logger.info(
            "Generating S3 URL | key=%s | download=%s",
            storage_key,
            download,
        )

        try:
            params = {
                "Bucket": self.bucket,
                "Key": storage_key,
            }

            if download:
                params["ResponseContentDisposition"] = (
                    f'attachment; filename="{filename}"'
                    if filename
                    else "attachment"
                )
            else:
                params["ResponseContentDisposition"] = "inline"

            url = self.client.generate_presigned_url(
                "get_object",
                Params=params,
                ExpiresIn=expires,
            )

        except ClientError:
            logger.exception(
                "S3 URL generation failed | key=%s",
                storage_key,
            )
            raise

        logger.info(
            "S3 URL generated | key=%s | download=%s",
            storage_key,
            download,
        )

        return url


storage = S3Storage()