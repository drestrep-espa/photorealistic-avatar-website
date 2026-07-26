import os
from pathlib import Path
from typing import Any

import boto3
from botocore.config import Config

from ..domain.file_storage_service import FileStorageService


class S3FileStorageService(FileStorageService):
    def __init__(
        self,
        *,
        bucket_name: str,
        client: Any | None = None,
        region_name: str | None = None,
    ) -> None:
        self._bucket_name = bucket_name
        resolved_region = (
            region_name
            or os.environ.get("AWS_REGION")
            or os.environ.get("AWS_DEFAULT_REGION")
        )
        self._client = client or boto3.client(
            "s3",
            region_name=resolved_region,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "virtual"},
            ),
        )

    def generate_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
        expires_in: int,
    ) -> str:
        return self._client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self._bucket_name,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )

    def download(self, *, object_key: str, destination_path: str) -> None:
        Path(destination_path).parent.mkdir(parents=True, exist_ok=True)
        self._client.download_file(
            self._bucket_name,
            object_key,
            destination_path,
        )

    def upload(
        self,
        *,
        source_path: str,
        object_key: str,
        content_type: str,
    ) -> None:
        self._client.upload_file(
            source_path,
            self._bucket_name,
            object_key,
            ExtraArgs={"ContentType": content_type},
        )

    def generate_download_url(self, *, object_key: str, expires_in: int) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self._bucket_name,
                "Key": object_key,
                "ResponseContentType": "application/pdf",
                "ResponseContentDisposition": (
                    'attachment; filename="informe_revision_normativa.pdf"'
                ),
            },
            ExpiresIn=expires_in,
        )
