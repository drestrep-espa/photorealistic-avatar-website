import json
from typing import Any, Callable, Dict, List, Optional

from ..domain.llm_service import LlmService


class Agent:
    def __init__(
        self,
        llm_service: LlmService,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_executors: Optional[Dict[str, Callable[[Dict[str, Any]], Any]]] = None,
        max_iterations: int = 10,
        system_prompt: Optional[str] = None,
        force_answer_on_max_iterations: bool = False,
    ) -> None:
        self._llm_service = llm_service
        self._tools = tools or []
        self._tool_executors = tool_executors or {}
        self._max_iterations = max_iterations
        self._force_answer_on_max_iterations = force_answer_on_max_iterations
        if system_prompt is not None:
            self._messages: List[Dict[str, Any]] = [
                {"role": "system", "content": system_prompt}
            ]
        else:
            self._messages = []

    def ask(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[str]:
        if history is not None:
            for item in history:
                self._messages.append(
                    {"role": item["role"], "content": item["content"]}
                )

        self._messages.append({"role": "user", "content": user_message})

        for round_number in range(1, self._max_iterations + 1):
            response = self._llm_service.make_request(
                self._messages, self._tools or None, tool_name="agent_reasoning"
            )
            self._print_reasoning(round_number, response.get("content"))
            tool_calls = response.get("tool_calls") or []

            if not tool_calls:
                self._messages.append({"role": "assistant", "content": response["content"]})
                return response["content"]

            self._messages.append(
                {
                    "role": "assistant",
                    "content": response["content"],
                    "tool_calls": [
                        {
                            "id": tool_call["id"],
                            "type": "function",
                            "function": {
                                "name": tool_call["name"],
                                "arguments": tool_call["arguments"],
                            },
                        }
                        for tool_call in tool_calls
                    ],
                }
            )

            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                if tool_name not in self._tool_executors:
                    raise RuntimeError(
                        f"La tool '{tool_name}' fue solicitada por el LLM pero no está "
                        "registrada en tool_executors."
                    )

                arguments = json.loads(tool_call["arguments"])
                result = self._tool_executors[tool_name](arguments)
                serialized_result = result if isinstance(result, str) else json.dumps(result)

                self._messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": serialized_result,
                    }
                )

        if self._force_answer_on_max_iterations:
            response = self._llm_service.make_request(
                self._messages, None, tool_name="agent_reasoning"
            )
            self._messages.append(
                {"role": "assistant", "content": response["content"]}
            )
            return response["content"]

        raise RuntimeError(
            f"Se alcanzó el número máximo de iteraciones ({self._max_iterations}) "
            "sin obtener una respuesta final del LLM."
        )

    def _print_reasoning(self, round_number: int, content: Optional[str]) -> None:
        if content:
            print(
                f"[agente] Ronda {round_number} — razonamiento: {content}",
                flush=True,
            )
