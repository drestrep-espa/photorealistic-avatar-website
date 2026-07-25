import os
from typing import Any, Dict, List, Optional

from src.application.answer_normative_question import (
    NORMATIVE_QA_SYSTEM_PROMPT,
    answer_normative_question,
)
from src.application.build_review_plan import BUILD_REVIEW_PLAN_TOOL, build_review_plan
from src.application.delete_project_document_index import delete_project_document_index
from src.application.generate_review_report import generate_review_report
from src.application.index_project_document import index_project_document
from src.application.search_item import SEARCH_ITEM_TOOL, search_item
from src.application.search_project_document import (
    SEARCH_PROJECT_DOCUMENT_TOOL,
    search_project_document,
)
from src.application.use_case import check_document_with_agent
from src.infrastructure.agent import Agent
from src.infrastructure.fpdf_report_generator import FpdfReportGenerator
from src.infrastructure.openai_llm_cost_tracker import OpenAiLlmCostTracker
from src.infrastructure.openai_llm_service import OpenAiLlmService
from src.infrastructure.openai_normative_search_service import OpenAiNormativeSearchService
from src.infrastructure.openai_project_document_search_service import (
    OpenAiProjectDocumentSearchService,
)


def check_document(document_path: str):
    api_key = os.environ["OPENAI_API_KEY"]
    vector_store_id = os.environ["VECTOR_STORE_id"]

    cost_tracker = OpenAiLlmCostTracker()
    llm_service = OpenAiLlmService(api_key=api_key, cost_tracker=cost_tracker)
    normative_search_service = OpenAiNormativeSearchService(
        api_key=api_key, vector_store_id=vector_store_id
    )

    project_document_search_service = OpenAiProjectDocumentSearchService(api_key=api_key)

    print(f"[flujo] Indexando el proyecto '{document_path}'...", flush=True)
    index_project_document(
        project_document_search_service=project_document_search_service,
        document_path=document_path,
    )
    print("[flujo] Proyecto indexado. Ejecutando la revisión con el agente...", flush=True)

    tools = [BUILD_REVIEW_PLAN_TOOL, SEARCH_ITEM_TOOL, SEARCH_PROJECT_DOCUMENT_TOOL]

    def run_build_review_plan(arguments):
        print(f"[tool] build_review_plan  args={arguments}", flush=True)
        return build_review_plan(llm_service=llm_service, document_path=document_path)

    def run_search_item(arguments):
        print(f"[tool] search_item  args={arguments}", flush=True)
        max_results = max(arguments.get("max_results", 15), 15)
        result = search_item(
            normative_search_service=normative_search_service,
            query=arguments["query"],
            max_results=max_results,
        )
        print(f"[tool] search_item -> {len(result)} fragmento(s) de normativa", flush=True)
        return result

    def run_search_project_document(arguments):
        print(f"[tool] search_project_document  args={arguments}", flush=True)
        result = search_project_document(
            project_document_search_service=project_document_search_service,
            query=arguments["query"],
            max_results=arguments.get("max_results", 8),
        )
        print(
            f"[tool] search_project_document -> {len(result)} fragmento(s) del proyecto",
            flush=True,
        )
        return result

    tool_executors = {
        "build_review_plan": run_build_review_plan,
        "search_item": run_search_item,
        "search_project_document": run_search_project_document,
    }

    agent = Agent(llm_service, tools=tools, tool_executors=tool_executors)

    try:
        resultado = check_document_with_agent(agent)
        print("[flujo] Revisión terminada. Generando el informe en PDF...", flush=True)
        report_path = generate_review_report(
            report_generator=FpdfReportGenerator(),
            content=resultado,
            output_dir="data/informe",
        )
        print(f"[flujo] Informe generado en '{report_path}'.", flush=True)
    finally:
        delete_project_document_index(
            project_document_search_service=project_document_search_service
        )

    return {
        "summary": resultado,
        "report_path": report_path,
        "cost_summary": cost_tracker.summary(),
    }


def answer_question(question: str, history: Optional[List[Dict[str, Any]]] = None):
    api_key = os.environ["OPENAI_API_KEY"]
    vector_store_id = os.environ["VECTOR_STORE_id"]

    cost_tracker = OpenAiLlmCostTracker()
    llm_service = OpenAiLlmService(api_key=api_key, cost_tracker=cost_tracker, model="gpt-5.4")
    normative_search_service = OpenAiNormativeSearchService(
        api_key=api_key, vector_store_id=vector_store_id
    )

    def run_search_item(arguments):
        print(f"[tool] search_item  args={arguments}", flush=True)
        max_results = max(arguments.get("max_results", 20), 20)
        result = search_item(
            normative_search_service=normative_search_service,
            query=arguments["query"],
            max_results=max_results,
        )
        print(f"[tool] search_item -> {len(result)} fragmento(s) de normativa", flush=True)
        return result

    agent = Agent(
        llm_service,
        tools=[SEARCH_ITEM_TOOL],
        tool_executors={"search_item": run_search_item},
        max_iterations=4,
        system_prompt=NORMATIVE_QA_SYSTEM_PROMPT,
        force_answer_on_max_iterations=True,
    )

    answer = answer_normative_question(agent=agent, question=question, history=history)
    return {"answer": answer, "cost_summary": cost_tracker.summary()}
