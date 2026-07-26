from pathlib import Path

from src.domain.file_storage_service import FileStorageService


class FakeFileStorageService(FileStorageService):
    def __init__(self, downloaded_content: bytes = b"%PDF-1.4 fake") -> None:
        self._downloaded_content = downloaded_content
        self.upload_url: str | None = None
        self.download_url: str | None = None
        self.received_upload_url_args: dict | None = None
        self.received_download_args: dict | None = None
        self.received_upload_args: dict | None = None
        self.received_download_url_args: dict | None = None

    def generate_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
        expires_in: int,
    ) -> str:
        self.received_upload_url_args = {
            "object_key": object_key,
            "content_type": content_type,
            "expires_in": expires_in,
        }
        self.upload_url = f"https://uploads.example/{object_key}"
        return self.upload_url

    def download(self, *, object_key: str, destination_path: str) -> None:
        self.received_download_args = {
            "object_key": object_key,
            "destination_path": destination_path,
        }
        destination = Path(destination_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(self._downloaded_content)

    def upload(
        self,
        *,
        source_path: str,
        object_key: str,
        content_type: str,
    ) -> None:
        self.received_upload_args = {
            "source_path": source_path,
            "object_key": object_key,
            "content_type": content_type,
        }

    def generate_download_url(self, *, object_key: str, expires_in: int) -> str:
        self.received_download_url_args = {
            "object_key": object_key,
            "expires_in": expires_in,
        }
        self.download_url = f"https://downloads.example/{object_key}"
        return self.download_url
