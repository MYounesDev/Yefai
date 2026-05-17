"""Chat router — manages conversational RAG sessions and messages."""

# Chat router placeholder — Phase 3A
import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from supabase import Client

from ai.novavision.inference import infer
from ai.novavision.preprocessing import resolve_image_path
from ai.novavision.schemas import InferenceRequest, InferenceResult
from ai.puqai.schemas import NotificationRequest
from auth.dependencies import get_org_context, require_permission
from auth.models import OrgContext
from auth.permissions import Permission
from db.client import get_supabase_client
from services.chat_service import ChatService
from services.notification_service import NotificationService
from services.prediction_service import PredictionService
from services.vector_search_service import VectorSearchService

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
        session = await service.create_session(org.org_id, org.user.id, body.title or "New Chat")
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
        messages = await service.get_session_messages(session_id, org.org_id, org.user.id)
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

    novavision_result: InferenceResult | None = None
    try:
        image_path = resolve_image_path(image_name)
        novavision_result = await infer(InferenceRequest(image_path=str(image_path)))
        if novavision_result.raw_response and novavision_result.raw_response.get(
            "normalized_image_path"
        ):
            logger.info(
                "Novavision normalized image saved: %s",
                novavision_result.raw_response["normalized_image_path"],
            )
    except (FileNotFoundError, ValueError) as e:
        logger.warning("Novavision preprocessing skipped: %s", e)
    except Exception as e:
        logger.warning("Novavision preprocessing failed: %s", e)

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
        prediction = await _run_prediction(
            set_id=image_data.get("set_id", 0),
            set_name=image_data.get("set_name", ""),
        )

        result = analyzer.analyze_anomaly(
            query_embedding=query_embedding,
            image_name=image_name,
            anomaly_score=anomaly_score,
            wear_type=wear_type,
            wear_value_um=wear_value_um,
            top_k=top_k,
            language=language,
            prediction=prediction,
        )
        if prediction and "error" not in prediction:
            result["prediction"] = prediction

        if novavision_result:
            result["novavision"] = {
                "job_id": novavision_result.job_id,
                "mock": novavision_result.mock,
                "processing_time_ms": novavision_result.processing_time_ms,
                "model_id": novavision_result.model_id,
                "normalized_image_path": novavision_result.raw_response.get("normalized_image_path")
                if novavision_result.raw_response
                else None,
                "node_statuses": novavision_result.raw_response.get("node_statuses")
                if novavision_result.raw_response
                else None,
            }

        _fire_puqai_webhook(
            image_data=image_data,
            anomaly_score=anomaly_score,
            wear_type=wear_type,
            wear_value_um=wear_value_um,
            image_name=image_name,
            llm_analysis=result.get("llm_analysis", ""),
            prediction=prediction,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Chat analyze failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


async def _run_prediction(set_id: int, set_name: str = "") -> dict[str, Any] | None:
    if not set_id and not set_name:
        return None

    machine_id = set_name

    try:
        from db.client import get_supabase_client

        client = get_supabase_client()
        if client is None:
            return None

        if not machine_id and set_id:
            resp = client.table("sets").select("name").eq("id", set_id).execute()
            if resp.data:
                machine_id = resp.data[0]["name"]

        if not machine_id:
            machine_id = f"Set{set_id}"

        svc = PredictionService(client)
        result = await svc.get_prediction(machine_id)
        return result
    except Exception:
        logger.exception("Prediction failed for %s", machine_id)
        return None


def _format_prediction_message(prediction: dict[str, Any]) -> str:
    hours = prediction.get("hours_to_critical", 0)
    confidence = prediction.get("confidence", "unknown")
    trend = prediction.get("trend", "unknown")
    current_wear = prediction.get("current_wear_um", 0)

    trend_labels: dict[str, str] = {
        "accelerating": "Hizlaniyor",
        "stable": "Sabit",
        "decelerating": "Yavasliyor",
    }

    conf_labels: dict[str, str] = {
        "high": "Yuksek",
        "medium": "Orta",
        "low": "Dusuk",
    }

    lines = [
        "📊 Asinma Tahmini",
        f"Mevcut Asinma: {current_wear:.0f} µm",
        f"Kritik Esige Kalan Sure: {hours:.1f} saat",
        f"Trend: {trend_labels.get(trend, trend)}",
        f"Guven: {conf_labels.get(confidence, confidence)}",
    ]

    scenarios = prediction.get("scenarios", {})
    if scenarios:
        base = scenarios.get("baseline", {})
        pess = scenarios.get("pessimistic", {})
        opt = scenarios.get("optimistic", {})
        lines.append(
            f"Senaryolar: Normal={base.get('hours', 0):.1f}h"
            f" / Kotu={pess.get('hours', 0):.1f}h"
            f" / Iyi={opt.get('hours', 0):.1f}h"
        )

    return "\n".join(lines)


def _fire_puqai_webhook(
    image_data: dict[str, Any],
    anomaly_score: float,
    wear_type: str,
    wear_value_um: float,
    image_name: str,
    llm_analysis: str = "",
    prediction: dict[str, Any] | None = None,
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

    if prediction and "error" not in prediction:
        pred_text = _format_prediction_message(prediction)
        message += f"\n\n{pred_text}"

        machine_id = prediction.get("machine_id", "")
        from db.config import get_settings

        settings_obj = get_settings()
        base_url = (
            getattr(settings_obj, "public_base_url", "http://localhost:8001")
            or "http://localhost:8001"
        )
        chart_url = f"{base_url}/api/predictions/{machine_id}/chart"
        message += f"\n\n📈 Asinma Grafigi: {chart_url}"

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
