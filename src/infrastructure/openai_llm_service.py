import base64
import os
from typing import Any, Dict, List, Optional

import openai

from ..domain.llm_service import LlmService


class OpenAiLlmService(LlmService):
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5.4-mini",
        client: Optional[openai.OpenAI] = None,
    ) -> None:
        self._model = model
        self._client = client or openai.OpenAI(api_key=api_key)

    def make_request(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        document_path: Optional[str] = None,
        expects_json: bool = False,
    ) -> Dict[str, Any]:
        request_messages = messages
        if document_path is not None:
            request_messages = self._attach_document_to_messages(
                messages, document_path
            )

        request_kwargs: Dict[str, Any] = {
            "model": self._model,
            "messages": request_messages,
            "tools": tools,
        }
        if expects_json:
            request_kwargs["response_format"] = {"type": "json_object"}

        response = self._client.chat.completions.create(**request_kwargs)
        message = response.choices[0].message

        return {
            "content": message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                }
                for tool_call in (message.tool_calls or [])
            ],
        }

    def _attach_document_to_messages(
        self, messages: List[Dict[str, Any]], document_path: str
    ) -> List[Dict[str, Any]]:
        # La API de Chat Completions de OpenAI (SDK openai==2.46.0) soporta un
        # content part de tipo "file" con "file_data" en formato data URI
        # (ver openai/types/chat/chat_completion_content_part_param.py::File).
        # El modelo procesa el PDF adjunto extrayendo tanto el texto como las
        # imágenes/planos que contiene, sin necesidad de OCR previo.
        file_content_part = self._build_file_content_part(document_path)
        updated_messages = [dict(message) for message in messages]
        last_message = updated_messages[-1]
        existing_content = last_message.get("content")
        if isinstance(existing_content, str):
            content_parts: List[Dict[str, Any]] = [
                {"type": "text", "text": existing_content}
            ]
        elif isinstance(existing_content, list):
            content_parts = list(existing_content)
        else:
            content_parts = []
        content_parts.append(file_content_part)
        last_message["content"] = content_parts
        return updated_messages

    def _build_file_content_part(self, document_path: str) -> Dict[str, Any]:
        with open(document_path, "rb") as document_file:
            encoded_document = base64.b64encode(document_file.read()).decode("utf-8")
        filename = os.path.basename(document_path)
        return {
            "type": "file",
            "file": {
                "filename": filename,
                "file_data": f"data:application/pdf;base64,{encoded_document}",
            },
        }
