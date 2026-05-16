"""Chat and RAG service — session management, hybrid search, message processing."""

import logging
from typing import Any

from supabase import Client

from services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class MockLLMService:
    """Mock LLM that generates contextual responses from retrieved data."""

    def generate_response(self, query: str, context: list[dict]) -> str:
        """
        Template-based response generation:
        - If context contains anomaly data → summarize anomaly findings
        - If context contains wear data → summarize prediction status
        - If context contains spare part data → summarize inventory/crisis
        - Default: general response about the system
        """
        if not context:
            return "I couldn't find specific information about that in the organization's data. Could you provide more details?"

        # Basic heuristic mapping based on source data
        source_types = [ctx.get("type", "unknown") for ctx in context]
        
        if "anomaly" in source_types or any("wear" in str(ctx) for ctx in context):
            return (
                f"Based on the data retrieved, there are wear anomalies detected. "
                f"The top context suggests an issue with severity {context[0].get('severity', 'unknown')}. "
                f"I recommend scheduling an immediate inspection."
            )
        elif "spare_part" in source_types or any("inventory" in str(ctx) for ctx in context):
            return (
                "Looking at the spare parts inventory, we have relevant components, but "
                "you should verify the lead times. Some parts might be on backorder."
            )
        
        return (
            f"Here is what I found regarding your query: The top result relates to "
            f"'{context[0].get('file_name', context[0].get('id', 'Unknown'))}'. "
            f"Does this help answer your question?"
        )


class ChatService:
    """Service for chat sessions, messages, and RAG search."""

    def __init__(self, supabase: Client, embedding_service: EmbeddingService | None = None):
        self.supabase = supabase
        self.embedding_service = embedding_service or EmbeddingService()
        self.llm = MockLLMService()

    async def create_session(self, org_id: str, user_id: str, title: str = "New Chat") -> dict:
        """Create a new chat session."""
        result = (
            self.supabase.table("chat_sessions")
            .insert({"org_id": org_id, "user_id": user_id, "title": title})
            .execute()
        )
        if not result.data:
            raise ValueError("Failed to create chat session")
        return result.data[0]

    async def get_sessions(self, org_id: str, user_id: str) -> list[dict]:
        """List user's chat sessions in this org."""
        result = (
            self.supabase.table("chat_sessions")
            .select("*")
            .eq("org_id", org_id)
            .eq("user_id", user_id)
            .eq("is_archived", False)
            .order("updated_at", desc=True)
            .execute()
        )
        return result.data or []

    async def get_session_messages(self, session_id: str, org_id: str, user_id: str) -> list[dict]:
        """Get all messages in a session. Validates ownership."""
        # Validate ownership
        session = (
            self.supabase.table("chat_sessions")
            .select("id")
            .eq("id", session_id)
            .eq("org_id", org_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        if not session.data:
            raise ValueError("Session not found or access denied")

        # Get messages
        result = (
            self.supabase.table("chat_messages")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .execute()
        )
        return result.data or []

    async def hybrid_search(self, org_id: str, query: str, top_k: int = 5) -> list[dict]:
        """Combine embedding similarity search + keyword search."""
        # 1. Embedding search via embedding_service
        try:
            vector_results = self.embedding_service.search_by_text(query, top_k=top_k, org_id=org_id)
        except RuntimeError:
            vector_results = []
        
        # In a real implementation, we would combine this with full-text search
        # on anomalies, purchase orders, etc.
        # For now, we return the vector search results mapped to standard context dicts.
        
        context = []
        for res in vector_results:
            context.append({
                "type": "image_anomaly",
                "id": res.get("image_name"),
                "similarity": res.get("similarity"),
                "wear": res.get("wear"),
                "set": res.get("set")
            })
            
        return context

    async def send_message(self, session_id: str, org_id: str, user_id: str, user_message: str) -> dict:
        """
        Process user message and generate LLM response using RAG.
        """
        # Validate ownership and get session
        session = (
            self.supabase.table("chat_sessions")
            .select("id")
            .eq("id", session_id)
            .eq("org_id", org_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        if not session.data:
            raise ValueError("Session not found or access denied")

        # 1. Save user message
        self.supabase.table("chat_messages").insert({
            "session_id": session_id,
            "role": "user",
            "content": user_message
        }).execute()
        
        # 2. Retrieve context via hybrid search
        context = await self.hybrid_search(org_id, user_message)

        # 3. Call Mock LLM
        llm_response = self.llm.generate_response(user_message, context)

        # 4. Save assistant response
        metadata = {"sources": context}
        assistant_result = self.supabase.table("chat_messages").insert({
            "session_id": session_id,
            "role": "assistant",
            "content": llm_response,
            "metadata": metadata
        }).execute()
        
        # Update session timestamp
        self.supabase.table("chat_sessions").update({
            "updated_at": "now()"
        }).eq("id", session_id).execute()

        if not assistant_result.data:
            raise ValueError("Failed to save assistant response")

        return assistant_result.data[0]

    async def archive_session(self, session_id: str, org_id: str, user_id: str) -> bool:
        """Soft delete a chat session."""
        result = (
            self.supabase.table("chat_sessions")
            .update({"is_archived": True, "updated_at": "now()"})
            .eq("id", session_id)
            .eq("org_id", org_id)
            .eq("user_id", user_id)
            .execute()
        )
        
        if not result.data:
            raise ValueError("Session not found or access denied")
        
        return True
