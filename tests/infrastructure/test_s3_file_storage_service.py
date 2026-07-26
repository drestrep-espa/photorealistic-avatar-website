from urllib.parse import parse_qs, urlparse

from src.domain.file_storage_service import FileStorageService
from src.infrastructure.s3_file_storage_service import S3FileStorageService


def test_s3_file_storage_service_implements_port(s3_client):
    service = S3FileStorageService(
        bucket_name="normativa-test-files",
        client=s3_client,
    )

    assert isinstance(service, FileStorageService)


def test_generate_upload_url_targets_object_and_expires_in_fifteen_minutes(s3_client):
    service = S3FileStorageService(
        bucket_name="normativa-test-files",
        client=s3_client,
    )

    url = service.generate_upload_url(
        object_key="uploads/project.pdf",
        content_type="application/pdf",
        expires_in=900,
    )

    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    assert parsed_url.path.endswith("/uploads/project.pdf")
    assert query["X-Amz-Expires"] == ["900"]


def test_default_client_generates_upload_url_with_ireland_regional_endpoint(
    s3_client,
):
    service = S3FileStorageService(bucket_name="normativa-test-files")

    url = service.generate_upload_url(
        object_key="uploads/project.pdf",
        content_type="application/pdf",
        expires_in=900,
    )

    assert urlparse(url).hostname == (
        "normativa-test-files.s3.eu-west-1.amazonaws.com"
    )


def test_download_writes_s3_object_to_destination(s3_client, tmp_path):
    s3_client.put_object(
        Bucket="normativa-test-files",
        Key="uploads/project.pdf",
        Body=b"%PDF-1.4 project",
        ContentType="application/pdf",
    )
    service = S3FileStorageService(
        bucket_name="normativa-test-files",
        client=s3_client,
    )
    destination = tmp_path / "project.pdf"

    service.download(
        object_key="uploads/project.pdf",
        destination_path=str(destination),
    )

    assert destination.read_bytes() == b"%PDF-1.4 project"


def test_upload_stores_pdf_with_expected_content_type(s3_client, tmp_path):
    report_path = tmp_path / "report.pdf"
    report_path.write_bytes(b"%PDF-1.4 report")
    service = S3FileStorageService(
        bucket_name="normativa-test-files",
        client=s3_client,
    )

    service.upload(
        source_path=str(report_path),
        object_key="reports/report.pdf",
        content_type="application/pdf",
    )

    stored = s3_client.get_object(
        Bucket="normativa-test-files",
        Key="reports/report.pdf",
    )
    assert stored["Body"].read() == b"%PDF-1.4 report"
    assert stored["ContentType"] == "application/pdf"


def test_generate_download_url_expires_in_two_hours(s3_client):
    service = S3FileStorageService(
        bucket_name="normativa-test-files",
        client=s3_client,
    )

    url = service.generate_download_url(
        object_key="reports/report.pdf",
        expires_in=7200,
    )

    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    assert parsed_url.path.endswith("/reports/report.pdf")
    assert query["X-Amz-Expires"] == ["7200"]
