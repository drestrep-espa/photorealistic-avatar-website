import json

import pytest

from tests.fakes.fake_llm_service import FakeLlmService

from src.application.build_review_plan import (
    _BUILD_REVIEW_PLAN_PROMPT,
    build_review_plan,
)


def _valid_plan_dict():
    return {
        "tipo_proyecto": {
            "municipio": "Boadilla del Monte",
            "uso": "residencial",
            "obra_nueva_o_reforma": "obra nueva",
            "ordenanza_aplicable": "unifamiliar aislada",
            "numero_viviendas": 1,
            "numero_plantas": 2,
        },
        "documentacion_esperada": ["memoria descriptiva", "estudio geotécnico"],
        "elementos_detectados": ["garaje", "piscina"],
        "normativa_aplicable": ["PGOU Boadilla del Monte", "CTE"],
        "usos_y_compatibilidad": "uso residencial compatible con la ordenanza",
        "parametros_urbanisticos_a_verificar": ["ocupación", "edificabilidad"],
        "justificaciones_tecnicas_requeridas": ["justificación de incendios"],
        "afecciones": ["arbolado protegido"],
        "coherencia_interna_a_revisar": ["municipio citado en memoria y anexos"],
        "afirmaciones_a_verificar": [
            {"afirmacion": "cumple retranqueos", "ubicacion": "memoria, pág. 12"}
        ],
        "puntos_no_automatizables": ["valoración estética de fachada"],
    }


def test_build_review_plan_returns_dict_from_llm_json_response():
    plan_dict = _valid_plan_dict()
    fake_llm_service = FakeLlmService(
        response={"content": json.dumps(plan_dict), "tool_calls": []}
    )

    result = build_review_plan(
        llm_service=fake_llm_service,
        document_path="/tmp/proyecto_basico.pdf",
    )

    assert result == plan_dict


def test_build_review_plan_sends_document_path_and_plain_prompt_content():
    fake_llm_service = FakeLlmService(
        response={"content": json.dumps(_valid_plan_dict()), "tool_calls": []}
    )
    document_path = "/tmp/proyecto_basico.pdf"

    build_review_plan(llm_service=fake_llm_service, document_path=document_path)

    assert fake_llm_service.received_document_path == document_path
    assert fake_llm_service.received_messages == [
        {"role": "user", "content": _BUILD_REVIEW_PLAN_PROMPT}
    ]


def test_build_review_plan_sends_tool_name_for_cost_tracking():
    fake_llm_service = FakeLlmService(
        response={"content": json.dumps(_valid_plan_dict()), "tool_calls": []}
    )

    build_review_plan(
        llm_service=fake_llm_service,
        document_path="/tmp/proyecto_basico.pdf",
    )

    assert fake_llm_service.received_tool_name == "build_review_plan"


def test_build_review_plan_propagates_json_decode_error_on_invalid_content():
    fake_llm_service = FakeLlmService(
        response={"content": "esto no es json", "tool_calls": []}
    )

    with pytest.raises(json.JSONDecodeError):
        build_review_plan(
            llm_service=fake_llm_service,
            document_path="/tmp/proyecto_basico.pdf",
        )
