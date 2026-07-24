import os

from src.application.build_review_plan import BUILD_REVIEW_PLAN_TOOL, build_review_plan
from src.application.index_project_document import index_project_document
from src.application.search_item import SEARCH_ITEM_TOOL, search_item
from src.application.search_project_document import (
    SEARCH_PROJECT_DOCUMENT_TOOL,
    search_project_document,
)
from src.application.use_case import check_document_with_agent
from src.infrastructure.agent import Agent
from src.infrastructure.openai_llm_cost_tracker import OpenAiLlmCostTracker
from src.infrastructure.openai_llm_service import OpenAiLlmService
from src.infrastructure.openai_normative_search_service import OpenAiNormativeSearchService
from src.infrastructure.openai_project_document_search_service import (
    OpenAiProjectDocumentSearchService,
)


def check_document(document_path: str):
    api_key = os.environ["OPENAI_API_KEY"]
    vector_store_id = os.environ["NORMATIVE_VECTOR_STORE_ID"]
    project_document_vector_store_id = os.environ.get("PROJECT_DOCUMENT_VECTOR_STORE_ID")

    cost_tracker = OpenAiLlmCostTracker()
    llm_service = OpenAiLlmService(api_key=api_key, cost_tracker=cost_tracker)
    normative_search_service = OpenAiNormativeSearchService(
        api_key=api_key, vector_store_id=vector_store_id
    )

    if project_document_vector_store_id is not None:
        project_document_search_service = OpenAiProjectDocumentSearchService(
            api_key=api_key, vector_store_id=project_document_vector_store_id
        )
    else:
        project_document_search_service = OpenAiProjectDocumentSearchService(api_key=api_key)

    if project_document_vector_store_id is None:
        index_project_document(
            project_document_search_service=project_document_search_service,
            document_path=document_path,
        )

    tools = [BUILD_REVIEW_PLAN_TOOL, SEARCH_ITEM_TOOL, SEARCH_PROJECT_DOCUMENT_TOOL]

    tool_executors = {
        "build_review_plan": lambda arguments: build_review_plan(
            llm_service=llm_service, document_path=document_path
        ),
        "search_item": lambda arguments: search_item(
            normative_search_service=normative_search_service,
            query=arguments["query"],
            max_results=arguments.get("max_results", 8),
        ),
        "search_project_document": lambda arguments: search_project_document(
            project_document_search_service=project_document_search_service,
            query=arguments["query"],
            max_results=arguments.get("max_results", 8),
        ),
    }

    agent = Agent(llm_service, tools=tools, tool_executors=tool_executors)
    resultado = check_document_with_agent(agent)
    return resultado, cost_tracker.summary()
