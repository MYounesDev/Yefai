# Chat router placeholder — Phase 3A
import asyncio
import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from ai.puqai.schemas import NotificationRequest
from services.notification_service import NotificationService
from services.vector_search_service import VectorSearchService
"""Chat router — manages conversational RAG sessions and messages."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from supabase import Client

from auth.dependencies import get_org_context, require_permission
from auth.models import OrgContext
from auth.permissions import Permission
from db.client import get_supabase_client
from services.chat_service import ChatService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

_embedding_svc = None


def _get_embedding_service():
    global _embedding_svc
    if _embedding_svc is None:
        from services.embedding_service import EmbeddingService

        _embedding_svc = EmbeddingService()
    return _embedding_svc


def _get_analyzer():
    from ai.langchain.analyzer import create_analyzer_from_env

    return create_analyzer_from_env()


def _get_vector_service():
    return VectorSearchService()


class CreateSessionRequest(BaseModel):
    title: str | None = "New Chat"


class SendMessageRequest(BaseModel):
    message: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


# ── Dependency ─────────────────────────────────────────────────


def _get_chat_service(supabase: Client = Depends(get_supabase_client)) -> ChatService:
    if supabase is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return ChatService(supabase)


# ── Endpoints ──────────────────────────────────────────────────

# ── Endpoints ──────────────────────────────────────────────────


@router.get("/sessions")
async def list_sessions(
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_CHAT)),
    service: ChatService = Depends(_get_chat_service),
) -> dict[str, Any]:
    """List the current user's chat sessions in this organization."""
    sessions = await service.get_sessions(org.org_id, org.user.id)
    return {"sessions": sessions}


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(
    body: CreateSessionRequest,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_CHAT)),
    service: ChatService = Depends(_get_chat_service),
) -> dict[str, Any]:
    """Create a new chat session."""
    try:
        session = await service.create_session(
            org.org_id, org.user.id, body.title or "New Chat"
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/sessions/{session_id}")
async def get_session_messages(
    session_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_CHAT)),
    service: ChatService = Depends(_get_chat_service),
) -> dict[str, Any]:
    """Get a chat session and all its messages."""
    try:
        messages = await service.get_session_messages(
            session_id, org.org_id, org.user.id
        )
        return {"session_id": session_id, "messages": messages}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    body: SendMessageRequest,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_CHAT)),
    service: ChatService = Depends(_get_chat_service),
) -> dict[str, Any]:
    """Send a message to a chat session and get a generated response."""
    try:
        assistant_message = await service.send_message(
            session_id, org.org_id, org.user.id, body.message
        )
        return assistant_message
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e



@router.delete("/sessions/{session_id}")
async def archive_session(
    session_id: str,
    org: OrgContext = Depends(get_org_context),
    service: ChatService = Depends(_get_chat_service),
) -> dict[str, str]:
    """Archive a chat session (soft delete)."""
    try:
        await service.archive_session(session_id, org.org_id, org.user.id)
        return {"message": "Session archived successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("/ask")
async def chat_ask(payload: dict[str, Any]) -> dict[str, Any]:
    question = payload.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    top_k = int(payload.get("top_k", 5))
    language = payload.get("language", "tr")

    try:
        embedding_svc = _get_embedding_service()
        if not embedding_svc.model_loaded and not embedding_svc.load_model():
            raise HTTPException(status_code=503, detail="Embedding model not loaded")

        from ai.embeddings.model import encode_text

        model = embedding_svc._model
        query_embedding = encode_text(model, question)

        analyzer = _get_analyzer()
        result = analyzer.chat(
            question=question,
            query_embedding=query_embedding,
            top_k=top_k,
            language=language,
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Chat ask failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/analyze")
async def chat_analyze(payload: dict[str, Any]) -> dict[str, Any]:
    image_name = payload.get("image_name", "").strip()
    anomaly_score = float(payload.get("anomaly_score", 0))
    wear_type = payload.get("wear_type", "")
    wear_value_um = float(payload.get("wear_value_um", 0))
    top_k = int(payload.get("top_k", 5))
    language = payload.get("language", "tr")

    if not image_name:
        raise HTTPException(status_code=400, detail="image_name is required")

    try:
        embedding_svc = _get_embedding_service()
        if not embedding_svc.model_loaded and not embedding_svc.load_model():
            raise HTTPException(status_code=503, detail="Embedding model not loaded")

        image_data = embedding_svc.get_image_embedding(image_name)
        if image_data is None:
            raise HTTPException(status_code=404, detail=f"Image not found: {image_name}")

        embedding = image_data.get("image_embedding")
        if not embedding:
            raise HTTPException(status_code=400, detail="Image has no embedding vector")

        if isinstance(embedding, str):
            import json

            query_embedding = json.loads(embedding)
        else:
            query_embedding = list(embedding)

        analyzer = _get_analyzer()
        result = analyzer.analyze_anomaly(
            query_embedding=query_embedding,
            image_name=image_name,
            anomaly_score=anomaly_score,
            wear_type=wear_type,
            wear_value_um=wear_value_um,
            top_k=top_k,
            language=language,
        )

        _fire_puqai_webhook(
            image_data=image_data,
            anomaly_score=anomaly_score,
            wear_type=wear_type,
            wear_value_um=wear_value_um,
            image_name=image_name,
            llm_analysis=result.get("llm_analysis", ""),
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Chat analyze failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


def _fire_puqai_webhook(
    image_data: dict[str, Any],
    anomaly_score: float,
    wear_type: str,
    wear_value_um: float,
    image_name: str,
    llm_analysis: str = "",
) -> None:
    from ai.puqai.config import get_puqai_settings

    settings = get_puqai_settings()
    if not settings.configured:
        return

    set_id = image_data.get("set_id", 0) or 0
    anomaly_id = image_data.get("id", 0) or 0
    set_name = image_data.get("set_name", "") or ""

    message = (
        f"🚨 Anomali Tespit Edildi\n"
        f"Gorsel: {image_name}\n"
        f"Skor: {anomaly_score}\n"
        f"Asinma Tipi: {wear_type}\n"
        f"Asinma Degeri: {wear_value_um} µm\n"
        f"Set: {set_name if set_name else f'set_{set_id}'}\n\n"
        f"{llm_analysis}"
    )

    request = NotificationRequest(
        anomaly_id=anomaly_id,
        score=anomaly_score,
        wear_type=wear_type,
        wear_value_um=wear_value_um,
        set_id=set_id,
        image_url=image_name,
        machine=set_name if set_name else f"set_{set_id}",
        message=message,
    )

    async def _send() -> None:
        svc = NotificationService()
        try:
            await svc.notify_anomaly(request)
            logger.info("PuqAI webhook sent for %s", image_name)
        except Exception:
            logger.exception("PuqAI webhook failed for %s", image_name)
        finally:
            await svc.close()

    asyncio.create_task(_send())


@router.post("/search")
async def chat_search(payload: dict[str, Any]) -> dict[str, Any]:
    text = payload.get("text", "").strip()
    top_k = int(payload.get("top_k", 5))
    min_similarity = float(payload.get("min_similarity", 0.0))

    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    try:
        embedding_svc = _get_embedding_service()
        if not embedding_svc.model_loaded and not embedding_svc.load_model():
            raise HTTPException(status_code=503, detail="Embedding model not loaded")

        from ai.embeddings.model import encode_text

        model = embedding_svc._model
        query_embedding = encode_text(model, text)

        vector_svc = _get_vector_service()
        result = vector_svc.search_similar_rich(
            query_embedding=query_embedding,
            top_k=top_k,
            min_similarity=min_similarity,
        )

        return {
            "query": text,
            "count": result.count,
            "results": [r.model_dump() for r in result.results],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Chat search failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e

