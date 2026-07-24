from typing import Any, Dict, List, Optional

from src.domain.llm_service import LlmService


class FakeLlmService(LlmService):
    def __init__(
        self,
        response: Optional[Dict[str, Any]] = None,
        responses: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        if responses is not None:
            self._responses = list(responses)
        else:
            self._responses = [response or {"content": "respuesta por defecto", "tool_calls": []}]
        self._call_count = 0
        self.received_messages: List[Dict[str, Any]] = []
        self.received_tools: Optional[List[Dict[str, Any]]] = None
        self.received_document_path: Optional[str] = None
        self.received_messages_per_call: List[List[Dict[str, Any]]] = []
        self.received_expects_json: bool = False

    def make_request(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        document_path: Optional[str] = None,
        expects_json: bool = False,
    ) -> Dict[str, Any]:
        self.received_messages = list(messages)
        self.received_tools = tools
        self.received_document_path = document_path
        self.received_messages_per_call.append(list(messages))
        self.received_expects_json = expects_json

        index = min(self._call_count, len(self._responses) - 1)
        self._call_count += 1
        return self._responses[index]
