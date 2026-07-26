from abc import ABC, abstractmethod


class FileStorageService(ABC):
    @abstractmethod
    def generate_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
        expires_in: int,
    ) -> str:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def download(self, *, object_key: str, destination_path: str) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def upload(
        self,
        *,
        source_path: str,
        object_key: str,
        content_type: str,
    ) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def generate_download_url(self, *, object_key: str, expires_in: int) -> str:
        raise NotImplementedError  # pragma: no cover
