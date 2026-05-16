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


# ── Request / Response Models ──────────────────────────────────


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


@router.post("/search")
async def hybrid_search(
    body: SearchRequest,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_CHAT)),
    service: ChatService = Depends(_get_chat_service),
) -> dict[str, Any]:
    """Test hybrid search directly (useful for UI debugging)."""
    try:
        results = await service.hybrid_search(org.org_id, body.query, body.top_k)
        return {"results": results}
    except Exception as e:
        logger.error("Hybrid search failed: %s", e)
        raise HTTPException(status_code=500, detail="Search failed") from e


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
