---
phase: 3A
name: "RAG Pipeline"
goal: "pgvector + LLM ile doğal dil sorgulama yapabilen RAG chatbot API'si. Streaming yanıt, hibrit arama, session yönetimi."
depends_on: "Phase 2A (embedding'ler pgvector'de)"
estimated_effort: "1.5 hafta"
manual_gate: "G4 — Gemini/Claude API key .env'de olmalı"
parallel: true
parallel_with: "Phase 3B"
assignee: "Kişi A"
---

# Plan: Phase 3A — RAG Pipeline

## Goal
Kullanıcı sorusunu embedding'e çevir, pgvector'de benzer görüntü/metadata bul, LLM'e context olarak ver, streaming yanıt döndür. Hibrit arama (vektör + SQL), session yönetimi. Sadece API — UI yok.

## Prerequisites (Manual Gate)
- [ ] **G4:** LLM API key alındı (Gemini Flash veya Claude sonnet)
- [ ] `LLM_API_KEY` ve `LLM_PROVIDER` `.env` dosyasında
- [ ] Phase 2A tamamlandı (embedding'ler pgvector'de)

---

## Tasks

### Wave 1: RAG Core Pipeline

#### Task 1.1: LLM client abstraction
- **Files:** `server/ai/llm/client.py`, `server/ai/llm/providers/`
- **Description:**
  - Abstraction layer: `LLMProvider` interface
  - Gemini Flash provider: `google-generativeai` SDK
  - Claude sonnet provider: `anthropic` SDK
  - `.env`'den provider seçimi: `LLM_PROVIDER=gemini|claude`
  - Streaming response: `async for chunk in stream`
  - Token counting + rate limit handling
- **UAT:** Her iki provider için streaming yanıt alınabiliyor

#### Task 1.2: RAG pipeline engine
- **Files:** `server/ai/rag/pipeline.py`
- **Description:**
  ```
  Kullanıcı sorusu
    → Jina CLIP v2 text embedding (Phase 2A'daki model)
    → pgvector cosine similarity search (top_k=5)
    → Metadata filtre (set, wear, date — SQL WHERE)
    → Context assembly:
       - İlgili görüntüler (local'den base64 — `data/MATWI/{file_path}`)
       - Metadata (wear, type, set, timestamp — Supabase'den)
       - Sensör verisi özeti (local CSV'lerden — opsiyonel)
    → LLM'e gönder: sistem prompt + context + soru
    → Streaming yanıt
  ```
  - Her adım için ayrı fonksiyon, test edilebilir
  - Context token limit kontrolü (LLM context window aşımı)
  - Fallback: embedding yoksa sadece metadata ile
- **UAT:** "Set 3'teki en yüksek aşınma?" sorusuna doğru yanıt

#### Task 1.3: Prompt template sistemi
- **Files:** `server/ai/rag/prompts.py`, `server/ai/rag/templates/`
- **Description:**
  - Sistem prompt'u: Rol (kestirimci bakım asistanı), veri seti bağlamı, yanıt formatı
  - Context template: görüntü + metadata formatı
  - Türkçe prompt (varsayılan)
  - Prompt değişkenleri: `{context}`, `{question}`, `{num_results}`
  - Template seçimi: config'den `RAG_PROMPT_TEMPLATE`
- **UAT:** Template'ler değişkenlerle doğru render ediliyor

### Wave 2: Hibrit Arama & Session

#### Task 2.1: Hibrit arama
- **Files:** `server/ai/rag/hybrid_search.py`
- **Description:**
  - Vektör similarity + SQL metadata filtresi tek sorguda
  - Örnek: "Set 5'teki flank wear görüntüleri" → embedding search + `WHERE set_id=5`
  - pgvector `<=>` operatörü + SQL WHERE
  - Filtre seçenekleri: set_id, wear_min, wear_max, type, date_from, date_to
  - Sonuç sıralama: similarity DESC, metadata'ya göre tiebreak
- **UAT:** Filtreli arama, filtresiz aramadan daha az ama daha alakalı sonuç dönüyor

#### Task 2.2: Chat session yönetimi
- **Files:** `server/ai/rag/sessions.py`
- **Description:**
  - Supabase `chat_sessions` ve `chat_messages` tabloları
  - Yeni session oluşturma
  - Mesaj geçmişi: soru-cevap çiftleri
  - Session bağlamı: son N mesajı context'e ekle (önceki sorulara referans)
  - Session expire: 24 saat sonra otomatik temizleme
- **UAT:** Session içinde önceki soruya referans verilebiliyor

### Wave 3: FastAPI Endpoint'leri

#### Task 3.1: Chat router (streaming SSE)
- **Files:** `server/routers/chat.py`, `server/services/chat_service.py`
- **Description:**
  - `POST /api/chat` — soru sor, streaming SSE yanıt
    - Request: `{ "question": "...", "session_id": "optional" }`
    - Response: `text/event-stream` (SSE format)
  - `GET /api/chat/sessions` — session listesi
  - `GET /api/chat/sessions/{session_id}` — session mesaj geçmişi
  - `DELETE /api/chat/sessions/{session_id}` — session sil
  - Rate limiting: IP başına 10 istek/dakika
- **UAT:** SSE streaming yanıt curl ile test edilebiliyor

#### Task 3.2: Search router
- **Files:** `server/routers/search.py`, `server/services/search_service.py`
- **Description:**
  - `POST /api/search/hybrid` — hibrit arama
    - Request: `{ "query": "...", "filters": { "set_id": 5, "type": "flank" }, "top_k": 10 }`
    - Response: görüntü listesi + metadata + similarity score
  - `POST /api/search/similar` — benzer görüntü bul (query image → benzerleri)
  - `GET /api/search/suggestions` — arama önerileri (sık sorulan sorular)
- **UAT:** Hibrit arama sonuçları alakalı ve hızlı (< 200ms)

---

## Verification

- [ ] RAG pipeline uçtan uca çalışıyor: soru → embedding → pgvector → LLM → yanıt
- [ ] Streaming SSE yanıt curl ile test edildi
- [ ] Hibrit arama vektör + metadata filtresi doğru çalışıyor
- [ ] Session yönetimi: mesaj geçmişi korunuyor, önceki soruya referans çalışıyor
- [ ] En az 10 örnek soru ile test edildi, yanıtlar doğru
- [ ] Turkish prompt ile Türkçe yanıt alınabiliyor

## must_haves

1. **RAG pipeline streaming çalışıyor** — Phase 4 entegrasyonu için
2. **pgvector similarity search < 50ms** — Kullanıcı deneyimi için
3. **Hibrit arama (vektör + metadata)** — Flexibıl sorgulama için
4. **LLM provider abstraction** — Gemini/Claude arası geçiş kolay
5. **SSE streaming** — Frontend'in streaming yanıt göstermesi için

## Deliverables
- `server/ai/llm/client.py` + `providers/gemini.py` + `providers/claude.py`
- `server/ai/rag/pipeline.py` + `prompts.py` + `templates/`
- `server/ai/rag/hybrid_search.py` + `sessions.py`
- `server/routers/chat.py` + `server/routers/search.py`
- `server/services/chat_service.py` + `server/services/search_service.py`
