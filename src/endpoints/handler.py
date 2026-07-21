


from src.application.use_case import check_document_with_agent
from src.infrastructure.agent import Agent
from src.infrastructure.openai_llm_service import OpenAiLlmService


def check_document():
    openai_service = OpenAiLlmService()
    agent = Agent(openai_service)
    return check_document_with_agent(agent)