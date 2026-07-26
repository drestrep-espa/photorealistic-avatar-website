import json
from functools import partial
from pathlib import Path
from unittest.mock import patch

from src.endpoints.review_lambda import handle_request, lambda_handler
from src.infrastructure.ssm_runtime_settings_loader import RuntimeSettings
from tests.fakes.fake_file_storage_service import FakeFileStorageService


def _post_event(path, body):
    return {
        "requestContext": {"http": {"method": "POST"}},
        "rawPath": path,
        "body": json.dumps(body),
    }


def test_upload_endpoint_returns_presigned_pdf_upload(tmp_path):
    storage = FakeFileStorageService()

    response = handle_request(
        _post_event(
            "/uploads",
            {"filename": "proyecto básico.pdf", "content_type": "application/pdf"},
        ),
        storage_service=storage,
        review_document_fn=lambda **kwargs: {},
        working_dir=str(tmp_path),
        id_factory=lambda: "upload-123",
    )

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body == {
        "upload_url": "https://uploads.example/uploads/upload-123.pdf",
        "document_key": "uploads/upload-123.pdf",
        "expires_in": 900,
    }
    assert storage.received_upload_url_args == {
        "object_key": "uploads/upload-123.pdf",
        "content_type": "application/pdf",
        "expires_in": 900,
    }


def test_upload_endpoint_rejects_non_pdf_files(tmp_path):
    response = handle_request(
        _post_event(
            "/uploads",
            {"filename": "proyecto.txt", "content_type": "text/plain"},
        ),
        storage_service=FakeFileStorageService(),
        review_document_fn=lambda **kwargs: {},
        working_dir=str(tmp_path),
    )

    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {
        "detail": "El fichero debe ser un PDF."
    }


def test_review_endpoint_generates_uploads_and_returns_report_url(tmp_path):
    storage = FakeFileStorageService()
    received = {}

    def review_document(document_path, report_output_dir):
        received["document_path"] = document_path
        received["report_output_dir"] = report_output_dir
        report_path = Path(report_output_dir) / "generated.pdf"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_bytes(b"%PDF-1.4 report")
        return {
            "summary": "resultado final",
            "report_path": str(report_path),
            "cost_summary": {"total_cost_usd": 0.25},
        }

    response = handle_request(
        _post_event("/reviews", {"document_key": "uploads/upload-123.pdf"}),
        storage_service=storage,
        review_document_fn=review_document,
        working_dir=str(tmp_path),
        id_factory=lambda: "review-456",
    )

    body = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert body == {
        "summary": "resultado final",
        "report_url": "https://downloads.example/reports/review-456.pdf",
        "expires_in": 7200,
        "cost_summary": {"total_cost_usd": 0.25},
    }
    assert storage.received_download_args["object_key"] == "uploads/upload-123.pdf"
    assert received["document_path"].endswith("upload-123.pdf")
    assert received["report_output_dir"] == str(tmp_path / "reports")
    assert storage.received_upload_args == {
        "source_path": str(tmp_path / "reports" / "generated.pdf"),
        "object_key": "reports/review-456.pdf",
        "content_type": "application/pdf",
    }
    assert storage.received_download_url_args == {
        "object_key": "reports/review-456.pdf",
        "expires_in": 7200,
    }


def test_review_endpoint_rejects_keys_outside_uploads_prefix(tmp_path):
    response = handle_request(
        _post_event("/reviews", {"document_key": "reports/other.pdf"}),
        storage_service=FakeFileStorageService(),
        review_document_fn=lambda **kwargs: {},
        working_dir=str(tmp_path),
    )

    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {
        "detail": "La clave del documento no es válida."
    }


def test_lambda_handler_injects_ssm_settings_into_review_handler(monkeypatch):
    monkeypatch.setenv("FILES_BUCKET", "normativa-files")
    settings = RuntimeSettings(
        openai_api_key="fake-openai-api-key",
        vector_store_id="fake-vector-store-id",
    )

    with (
        patch("src.endpoints.review_lambda.runtime_settings_loader") as loader,
        patch("src.endpoints.review_lambda.S3FileStorageService"),
        patch("src.endpoints.review_lambda.handle_request") as request_handler,
    ):
        loader.load.return_value = settings

        lambda_handler(_post_event("/reviews", {"document_key": "uploads/a.pdf"}), None)

    _, kwargs = request_handler.call_args
    review_document_fn = kwargs["review_document_fn"]
    assert isinstance(review_document_fn, partial)
    assert review_document_fn.keywords == {
        "api_key": "fake-openai-api-key",
        "vector_store_id": "fake-vector-store-id",
    }
