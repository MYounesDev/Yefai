-- Yefai Phase B5 — Chat and RAG Tables
-- Chat sessions and messages for multi-turn conversations

-- ============================================================
-- Chat Sessions
-- ============================================================

CREATE TABLE IF NOT EXISTS chat_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL,
    title           TEXT DEFAULT 'New Chat',
    is_archived     BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_org_id ON chat_sessions(org_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);

-- ============================================================
-- Chat Messages
-- ============================================================

CREATE TABLE IF NOT EXISTS chat_messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role            TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content         TEXT NOT NULL,
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);

-- ============================================================
-- Comments
-- ============================================================

COMMENT ON TABLE chat_sessions IS 'Conversational sessions for RAG chat';
COMMENT ON TABLE chat_messages IS 'Individual messages within a chat session';
COMMENT ON COLUMN chat_messages.metadata IS 'Stores sources, retrieved context, and UI hints';
