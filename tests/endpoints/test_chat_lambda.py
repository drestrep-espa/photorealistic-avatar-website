import json
from unittest.mock import patch

from src.endpoints.chat_lambda import handle_request, lambda_handler
from src.infrastructure.ssm_runtime_settings_loader import RuntimeSettings


def _post_event(body):
    return {
        "requestContext": {"http": {"method": "POST"}},
        "rawPath": "/questions",
        "body": json.dumps(body),
    }


def test_chat_lambda_forwards_question_and_history():
    received = {}

    def answer_question(question, history):
        received["question"] = question
        received["history"] = history
        return {
            "answer": "La **ocupación máxima** es 45 %.",
            "cost_summary": {"total_cost_usd": 0.01},
        }

    response = handle_request(
        _post_event(
            {
                "question": "¿Cuál es la ocupación máxima?",
                "history": [{"role": "user", "content": "En RU-3"}],
            }
        ),
        answer_question_fn=answer_question,
    )

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["answer"] == "La **ocupación máxima** es 45 %."
    assert received == {
        "question": "¿Cuál es la ocupación máxima?",
        "history": [{"role": "user", "content": "En RU-3"}],
    }


def test_chat_lambda_rejects_empty_question():
    response = handle_request(
        _post_event({"question": "  ", "history": []}),
        answer_question_fn=lambda **kwargs: {},
    )

    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {
        "detail": "La pregunta no puede estar vacía."
    }


def test_chat_lambda_rejects_non_post_requests():
    response = handle_request(
        {
            "requestContext": {"http": {"method": "GET"}},
            "rawPath": "/questions",
        },
        answer_question_fn=lambda **kwargs: {},
    )

    assert response["statusCode"] == 405


def test_lambda_handler_injects_ssm_settings_into_question_handler():
    settings = RuntimeSettings(
        openai_api_key="fake-openai-api-key",
        vector_store_id="fake-vector-store-id",
    )

    with (
        patch("src.endpoints.chat_lambda.runtime_settings_loader") as loader,
        patch("src.endpoints.chat_lambda.answer_question") as answer_question,
    ):
        loader.load.return_value = settings
        answer_question.return_value = {
            "answer": "Siete metros.",
            "cost_summary": {"total_cost_usd": 0.01},
        }

        lambda_handler(_post_event({"question": "altura"}), None)

    answer_question.assert_called_once_with(
        question="altura",
        history=[],
        api_key="fake-openai-api-key",
        vector_store_id="fake-vector-store-id",
    )
