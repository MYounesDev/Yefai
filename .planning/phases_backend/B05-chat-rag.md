# Phase B5 — Chat/RAG Service

> Implement the RAG chatbot backend (Phase 3A from ROADMAP.md). Replace the placeholder `routers/chat.py` with a full chat service using embeddings + LLM.

## Context

The embedding service (`ai/embeddings/`) already works — it can search images by text/image using Jina CLIP v2 and pgvector. The chat service builds ON TOP of this, adding:
1. Chat session management (multi-turn)
2. Hybrid search (embedding similarity + keyword)
3. LLM response generation (PUQ AI or local model)
4. Context-aware answers using retrieved documents + images

## Task

### 1. Chat Tables (`db/migrations/007_chat_tables.sql`)

```sql
CREATE TABLE IF NOT EXISTS chat_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL,
    title           TEXT DEFAULT 'New Chat',
    is_archived     BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role            TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content         TEXT NOT NULL,
    metadata        JSONB DEFAULT '{}'::jsonb,
    -- metadata can contain: { sources: [...], images: [...], search_query: "..." }
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_org_id ON chat_sessions(org_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
```

### 2. Chat Service (`services/chat_service.py`)

```python
class ChatService:
    def __init__(self, supabase: Client, embedding_service: EmbeddingService):
        self.supabase = supabase
        self.embedding_service = embedding_service

    async def create_session(self, org_id: str, user_id: str) -> dict:
        """Create a new chat session."""

    async def get_sessions(self, org_id: str, user_id: str) -> list[dict]:
        """List user's chat sessions in this org."""

    async def get_session_messages(self, session_id: str) -> list[dict]:
        """Get all messages in a session."""

    async def send_message(
        self, session_id: str, org_id: str, user_message: str
    ) -> dict:
        """
        Process user message:
        1. Save user message to chat_messages
        2. Retrieve context via hybrid search (embedding + keyword)
        3. Build prompt with retrieved context
        4. Call LLM (PUQ AI or mock)
        5. Save assistant response to chat_messages
        6. Return response with sources
        """

    async def hybrid_search(
        self, org_id: str, query: str, filters: dict = None
    ) -> list[dict]:
        """
        Combine embedding similarity search + keyword search:
        1. Embedding search via embedding_service (pgvector cosine similarity)
        2. Keyword/metadata search (SQL LIKE/ILIKE on anomalies, spare_parts)
        3. Merge + deduplicate + rank results
        Return top-K results with relevance scores.
        """
```

### 3. Chat Router (`routers/chat.py`)

Replace the placeholder:

```python
router = APIRouter(prefix="/api/chat", tags=["chat"])

GET /api/chat/sessions
  Auth: Bearer + org member + VIEW_CHAT permission
  → List user's chat sessions (org-scoped)

POST /api/chat/sessions
  Auth: VIEW_CHAT permission
  → Create new session, return { session_id, title, created_at }

GET /api/chat/sessions/{session_id}
  Auth: VIEW_CHAT permission + session owner
  → Get session with all messages

POST /api/chat/sessions/{session_id}/messages
  Auth: VIEW_CHAT permission
  Body: { message: string }
  → Process message, return assistant response with sources
  → Response: { id, role: "assistant", content, metadata: { sources: [...] } }

POST /api/chat/search
  Auth: VIEW_CHAT permission
  Body: { query, filters?: { wear_type?, severity?, date_range? } }
  → Hybrid search across org data
  → Return ranked results with snippets

DELETE /api/chat/sessions/{session_id}
  Auth: session owner
  → Archive session (soft delete)
```

### 4. LLM Integration

For now, implement a mock LLM response generator:
- Take user query + retrieved context
- Generate a structured response using templates
- In production: will call PUQ AI API or local model

```python
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
```

## Deliverables

- [ ] `db/migrations/007_chat_tables.sql` — chat_sessions + chat_messages tables
- [ ] `services/chat_service.py` — session management, hybrid search, message processing
- [ ] `routers/chat.py` — full chat API (sessions, messages, search)
- [ ] Mock LLM response generator
- [ ] Chat sessions are org-scoped and user-scoped
- [ ] Hybrid search works (embedding + keyword)
- [ ] Auth + permission checks on all endpoints
- [ ] `main.py` updated to include chat router
