import base64
import json
import logging
import os
import shutil
import uuid
from collections.abc import Callable
from functools import partial
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from src.domain.file_storage_service import FileStorageService
from src.endpoints.handler import check_document
from src.infrastructure.s3_file_storage_service import S3FileStorageService
from src.infrastructure.ssm_runtime_settings_loader import runtime_settings_loader

PDF_CONTENT_TYPE = "application/pdf"
UPLOAD_URL_EXPIRATION_SECONDS = 900
DOWNLOAD_URL_EXPIRATION_SECONDS = 7200

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    settings = runtime_settings_loader.load()
    storage_service = S3FileStorageService(bucket_name=os.environ["FILES_BUCKET"])
    return handle_request(
        event,
        storage_service=storage_service,
        review_document_fn=partial(
            check_document,
            api_key=settings.openai_api_key,
            vector_store_id=settings.vector_store_id,
        ),
    )


def handle_request(
    event: dict[str, Any],
    *,
    storage_service: FileStorageService,
    review_document_fn: Callable[..., dict[str, Any]],
    working_dir: str = "/tmp/normativa-precheck",
    id_factory: Callable[[], str] | None = None,
) -> dict[str, Any]:
    method = event.get("requestContext", {}).get("http", {}).get("method")
    if method != "POST":
        return _response(405, {"detail": "Método no permitido."})

    try:
        payload = _parse_json_body(event)
    except (JSONDecodeError, UnicodeDecodeError, TypeError):
        return _response(400, {"detail": "El cuerpo de la petición no es válido."})

    path = event.get("rawPath", "")
    create_id = id_factory or (lambda: uuid.uuid4().hex)

    if path.endswith("/uploads"):
        return _create_upload(payload, storage_service, create_id)
    if path.endswith("/reviews"):
        return _create_review(
            payload,
            storage_service=storage_service,
            review_document_fn=review_document_fn,
            working_dir=working_dir,
            create_id=create_id,
        )
    return _response(404, {"detail": "Ruta no encontrada."})


def _create_upload(
    payload: dict[str, Any],
    storage_service: FileStorageService,
    create_id: Callable[[], str],
) -> dict[str, Any]:
    filename = payload.get("filename")
    content_type = payload.get("content_type")
    if (
        not isinstance(filename, str)
        or not filename.lower().endswith(".pdf")
        or content_type != PDF_CONTENT_TYPE
    ):
        return _response(400, {"detail": "El fichero debe ser un PDF."})

    document_key = f"uploads/{create_id()}.pdf"
    upload_url = storage_service.generate_upload_url(
        object_key=document_key,
        content_type=PDF_CONTENT_TYPE,
        expires_in=UPLOAD_URL_EXPIRATION_SECONDS,
    )
    return _response(
        200,
        {
            "upload_url": upload_url,
            "document_key": document_key,
            "expires_in": UPLOAD_URL_EXPIRATION_SECONDS,
        },
    )


def _create_review(
    payload: dict[str, Any],
    *,
    storage_service: FileStorageService,
    review_document_fn: Callable[..., dict[str, Any]],
    working_dir: str,
    create_id: Callable[[], str],
) -> dict[str, Any]:
    document_key = payload.get("document_key")
    if (
        not isinstance(document_key, str)
        or not document_key.startswith("uploads/")
        or not document_key.endswith(".pdf")
        or ".." in document_key
    ):
        return _response(400, {"detail": "La clave del documento no es válida."})

    review_id = create_id()
    execution_dir = Path(working_dir)
    document_path = execution_dir / Path(document_key).name
    reports_dir = execution_dir / "reports"

    try:
        storage_service.download(
            object_key=document_key,
            destination_path=str(document_path),
        )
        result = review_document_fn(
            document_path=str(document_path),
            report_output_dir=str(reports_dir),
        )
        report_key = f"reports/{review_id}.pdf"
        storage_service.upload(
            source_path=result["report_path"],
            object_key=report_key,
            content_type=PDF_CONTENT_TYPE,
        )
        report_url = storage_service.generate_download_url(
            object_key=report_key,
            expires_in=DOWNLOAD_URL_EXPIRATION_SECONDS,
        )
        return _response(
            200,
            {
                "summary": result["summary"],
                "report_url": report_url,
                "expires_in": DOWNLOAD_URL_EXPIRATION_SECONDS,
                "cost_summary": result["cost_summary"],
            },
        )
    except Exception:
        logger.exception("Error al generar un informe normativo")
        return _response(500, {"detail": "No se pudo generar el informe."})
    finally:
        shutil.rmtree(execution_dir, ignore_errors=True)


def _parse_json_body(event: dict[str, Any]) -> dict[str, Any]:
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise TypeError
    return payload


def _response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "body": json.dumps(body, ensure_ascii=False),
    }
