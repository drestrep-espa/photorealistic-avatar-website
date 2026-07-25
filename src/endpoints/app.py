import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.endpoints.handler import answer_question, check_document

load_dotenv()

app = FastAPI(title="Pre-revisión normativa")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOADS_DIR = Path("data/uploads")


class ChatMessage(BaseModel):
    role: str
    content: str


class AskQuestionRequest(BaseModel):
    question: str
    history: list[ChatMessage] = []


def _print_cost(cost_summary: dict) -> None:
    total = cost_summary.get("total_cost_usd", 0.0)
    print(f"[coste] Total de esta ejecución: ${total:.4f}", flush=True)
    for tool_name, tool_stats in cost_summary.get("by_tool", {}).items():
        print(
            f"[coste]   - {tool_name}: ${tool_stats.get('cost_usd', 0.0):.4f} "
            f"({tool_stats.get('calls', 0)} llamada(s))",
            flush=True,
        )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/reviews")
async def create_review(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El fichero debe ser un PDF.")

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    document_path = UPLOADS_DIR / f"{uuid.uuid4().hex}_{file.filename}"
    document_path.write_bytes(await file.read())

    try:
        result = check_document(document_path=str(document_path))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    _print_cost(result["cost_summary"])
    return result


@app.post("/questions")
def ask_question(request: AskQuestionRequest):
    try:
        result = answer_question(
            question=request.question,
            history=[message.model_dump() for message in request.history],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    _print_cost(result["cost_summary"])
    return result
