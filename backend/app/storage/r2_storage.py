import boto3

from app.core.config import settings
from app.core.logging import logger


class R2Storage:

    def __init__(self):

        self.client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name="auto",
        )

        self.bucket = settings.R2_BUCKET_NAME

        logger.info(
            "R2 storage initialized | bucket=%s",
            self.bucket,
        )

    def upload_file(
        self,
        file_path: str,
        storage_key: str,
        content_type: str,
    ):

        logger.info(
            "R2 upload started | key=%s",
            storage_key,
        )

        self.client.upload_file(
            file_path,
            self.bucket,
            storage_key,
            ExtraArgs={
                "ContentType": content_type,
            },
        )

        logger.info(
            "R2 upload completed | key=%s",
            storage_key,
        )

    def upload_bytes(
        self,
        data: bytes,
        storage_key: str,
        content_type: str,
    ):

        logger.info(
            "R2 bytes upload started | key=%s",
            storage_key,
        )

        self.client.put_object(
            Bucket=self.bucket,
            Key=storage_key,
            Body=data,
            ContentType=content_type,
        )

        logger.info(
            "R2 bytes upload completed | key=%s",
            storage_key,
        )

    def download(
        self,
        storage_key: str,
    ) -> bytes:

        logger.info(
            "R2 download started | key=%s",
            storage_key,
        )

        response = self.client.get_object(
            Bucket=self.bucket,
            Key=storage_key,
        )

        data = response["Body"].read()

        logger.info(
            "R2 download completed | key=%s | size=%s",
            storage_key,
            len(data),
        )

        return data

    def delete(
        self,
        storage_key: str,
    ):

        logger.info(
            "R2 delete started | key=%s",
            storage_key,
        )

        self.client.delete_object(
            Bucket=self.bucket,
            Key=storage_key,
        )

        logger.info(
            "R2 delete completed | key=%s",
            storage_key,
        )

    def download_url(
        self,
        storage_key: str,
        expires: int = 3600,
    ) -> str:

        logger.info(
            "Generating R2 presigned URL | key=%s",
            storage_key,
        )

        url = self.client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket,
                "Key": storage_key,
            },
            ExpiresIn=expires,
        )

        logger.info(
            "R2 presigned URL generated | key=%s",
            storage_key,
        )

        return url


storage = R2Storage()
