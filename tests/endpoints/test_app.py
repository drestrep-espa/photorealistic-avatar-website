from pathlib import Path
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.endpoints.app import app

client = TestClient(app)


def _cleanup_uploads():
    uploads_dir = Path("data/uploads")
    if uploads_dir.exists():
        for uploaded_file in uploads_dir.iterdir():
            uploaded_file.unlink()


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_review_without_file_returns_422():
    response = client.post("/reviews")

    assert response.status_code == 422


def test_create_review_with_non_pdf_file_returns_400():
    try:
        response = client.post(
            "/reviews",
            files={"file": ("proyecto.txt", b"contenido de texto", "text/plain")},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "El fichero debe ser un PDF."
    finally:
        _cleanup_uploads()


@patch("src.endpoints.app.check_document")
def test_create_review_with_valid_pdf_returns_check_document_result(mock_check_document):
    mock_check_document.return_value = {
        "summary": "resultado final",
        "report_path": "data/informe/informe.pdf",
        "cost_summary": {"total_cost_usd": 0.0},
    }

    try:
        response = client.post(
            "/reviews",
            files={
                "file": (
                    "proyecto.pdf",
                    b"%PDF-1.4 contenido de prueba",
                    "application/pdf",
                )
            },
        )

        assert response.status_code == 200
        assert response.json() == mock_check_document.return_value

        mock_check_document.assert_called_once()
        _, kwargs = mock_check_document.call_args
        assert kwargs["document_path"].startswith("data/uploads/")
    finally:
        _cleanup_uploads()


@patch("src.endpoints.app.check_document")
def test_create_review_returns_500_when_check_document_raises(mock_check_document):
    mock_check_document.side_effect = RuntimeError("fallo al revisar el documento")

    try:
        response = client.post(
            "/reviews",
            files={
                "file": (
                    "proyecto.pdf",
                    b"%PDF-1.4 contenido de prueba",
                    "application/pdf",
                )
            },
        )

        assert response.status_code == 500
        assert response.json()["detail"] == "fallo al revisar el documento"
    finally:
        _cleanup_uploads()


@patch("src.endpoints.app.answer_question")
def test_ask_question_returns_answer(mock_answer_question):
    mock_answer_question.return_value = {
        "answer": "La altura máxima es 7 m (PGOU, art. 5).",
        "cost_summary": {"total_cost_usd": 0.0},
    }

    response = client.post(
        "/questions",
        json={"question": "¿altura máxima?", "history": []},
    )

    assert response.status_code == 200
    assert response.json() == mock_answer_question.return_value

    mock_answer_question.assert_called_once()
    _, kwargs = mock_answer_question.call_args
    assert kwargs["question"] == "¿altura máxima?"
    assert kwargs["history"] == []


@patch("src.endpoints.app.answer_question")
def test_ask_question_forwards_history(mock_answer_question):
    mock_answer_question.return_value = {
        "answer": "respuesta",
        "cost_summary": {"total_cost_usd": 0.0},
    }

    history = [
        {"role": "user", "content": "a"},
        {"role": "assistant", "content": "b"},
    ]

    response = client.post(
        "/questions",
        json={"question": "¿y ahora?", "history": history},
    )

    assert response.status_code == 200

    mock_answer_question.assert_called_once()
    _, kwargs = mock_answer_question.call_args
    assert kwargs["history"] == history


def test_ask_question_without_question_returns_422():
    response = client.post("/questions", json={})

    assert response.status_code == 422


@patch("src.endpoints.app.answer_question")
def test_ask_question_returns_500_when_handler_raises(mock_answer_question):
    mock_answer_question.side_effect = RuntimeError("fallo")

    response = client.post(
        "/questions",
        json={"question": "¿algo?", "history": []},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "fallo"
