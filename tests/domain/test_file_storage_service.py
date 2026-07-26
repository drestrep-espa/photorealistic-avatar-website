import pytest

from src.domain.file_storage_service import FileStorageService
from tests.fakes.fake_file_storage_service import FakeFileStorageService


def test_file_storage_service_cannot_be_instantiated():
    with pytest.raises(TypeError):
        FileStorageService()


def test_fake_file_storage_service_implements_the_port(tmp_path):
    service = FakeFileStorageService()
    destination_path = tmp_path / "project.pdf"

    upload_url = service.generate_upload_url(
        object_key="uploads/project.pdf",
        content_type="application/pdf",
        expires_in=900,
    )
    service.download(
        object_key="uploads/project.pdf",
        destination_path=str(destination_path),
    )
    service.upload(
        source_path=str(destination_path),
        object_key="reports/report.pdf",
        content_type="application/pdf",
    )
    download_url = service.generate_download_url(
        object_key="reports/report.pdf",
        expires_in=7200,
    )

    assert isinstance(service, FileStorageService)
    assert upload_url == "https://uploads.example/uploads/project.pdf"
    assert download_url == "https://downloads.example/reports/report.pdf"
