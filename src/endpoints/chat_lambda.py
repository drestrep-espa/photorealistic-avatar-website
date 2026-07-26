import base64
import json
import logging
from collections.abc import Callable
from functools import partial
from json import JSONDecodeError
from typing import Any

from src.endpoints.handler import answer_question
from src.infrastructure.ssm_runtime_settings_loader import runtime_settings_loader

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    settings = runtime_settings_loader.load()
    return handle_request(
        event,
        answer_question_fn=partial(
            answer_question,
            api_key=settings.openai_api_key,
            vector_store_id=settings.vector_store_id,
        ),
    )


def handle_request(
    event: dict[str, Any],
    *,
    answer_question_fn: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    method = event.get("requestContext", {}).get("http", {}).get("method")
    if method != "POST":
        return _response(405, {"detail": "Método no permitido."})

    try:
        payload = _parse_json_body(event)
    except (JSONDecodeError, UnicodeDecodeError, TypeError):
        return _response(400, {"detail": "El cuerpo de la petición no es válido."})

    question = payload.get("question")
    if not isinstance(question, str) or not question.strip():
        return _response(400, {"detail": "La pregunta no puede estar vacía."})

    history = payload.get("history", [])
    if not isinstance(history, list):
        return _response(400, {"detail": "El historial no es válido."})

    try:
        result = answer_question_fn(question=question.strip(), history=history)
    except Exception:
        logger.exception("Error al responder una pregunta normativa")
        return _response(500, {"detail": "No se pudo responder la pregunta."})

    return _response(200, result)


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
