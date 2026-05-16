---
phase: 4
name: "FastAPI Lifespan & Entegrasyon"
goal: "Tüm servisleri FastAPI lifespan altında birleştir, entegrasyon testleri, OpenAPI dokümantasyonu, production-ready hale getir."
depends_on: "Phase 3A, Phase 3B"
estimated_effort: "1 hafta"
manual_gate: ""
parallel: false
assignee: "birlikte"
---

# Plan: Phase 4 — FastAPI Lifespan & Entegrasyon

## Goal
Tüm router'ları tek FastAPI app altında birleştir. Lifespan ile startup/shutdown yönetimi. Entegrasyon testleri. OpenAPI (Swagger) dokümantasyonu. Production-ready konfigürasyon.

## Prerequisites
- [x] Phase 3A tamamlandı (RAG endpoint'leri hazır)
- [x] Phase 3B tamamlandı (PUQ AI + kriz endpoint'leri hazır)
- [x] Phase 2A tamamlandı (Anomalib + embedding endpoint'leri hazır)
- [x] Phase 2B tamamlandı (NovaVision endpoint'leri hazır)
- [ ] Tüm `.env` değişkenleri eksiksiz

---

## Tasks

### Wave 1: Lifespan Yönetimi

#### Task 1.1: FastAPI lifespan implementation
- **Files:** `server/main.py`, `server/lifespan.py`
- **Description:**
  ```python
  from contextlib import asynccontextmanager
  
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      # STARTUP
      logger.info("Starting Yefai server...")
      
      # 1. Config validasyonu
      validate_config()
      
      # 2. Supabase bağlantısı
      app.state.supabase = await create_supabase_client()
      await app.state.supabase.table("sets").select("count").execute()  # health check
      
      # 3. Model yükleme (lazy: ilk istekte)
      app.state.models = {}
      # app.state.models["jina_clip"] = load_jina_clip()  # opsiyonel eager loading
      
      # 4. NovaVision health check (opsiyonel)
      # await check_novavision_health()
      
      logger.info("Yefai server ready")
      yield
      
      # SHUTDOWN
      logger.info("Shutting down...")
      await app.state.supabase.aclose()
      # Model cleanup
      logger.info("Shutdown complete")
  
  app = FastAPI(lifespan=lifespan)
  ```
  - Graceful shutdown: aktif isteklerin tamamlanmasını bekle
  - Config validasyonu: eksik env var ise uyarı log'u, kritik olanlar için raise
- **UAT:** `uvicorn server.main:app` başlatıldığında startup log'ları görünür, CTRL+C ile graceful shutdown

#### Task 1.2: Config validasyonu
- **Files:** `server/config.py`
- **Description:**
  - pydantic-settings ile tüm config:
    ```python
    class Settings(BaseSettings):
        supabase_url: str
        supabase_service_key: str
        novavision_api_key: Optional[str] = None
        novavision_api_url: Optional[str] = None
        novavision_mock: bool = False
        puqai_anomaly_webhook: Optional[str] = None
        puqai_email_webhook: Optional[str] = None
        puqai_sms_webhook: Optional[str] = None
        llm_api_key: Optional[str] = None
        llm_provider: Literal["gemini", "claude"] = "gemini"
        embedding_dim: int = 1024
        anomaly_threshold: float = 0.7
        model_config = SettingsConfigDict(env_file=".env")
    ```
  - Startup'ta validasyon, eksikleri log'la
  - Kritik/non-kritik ayrımı
- **UAT:** Eksik `.env` ile başlatılınca anlamlı hata mesajı

### Wave 2: Router Entegrasyonu

#### Task 2.1: Tüm router'ları bağlama
- **Files:** `server/main.py`
- **Description:**
  ```python
  from server.routers import (
      anomalib, novavision, embeddings,
      chat, search, notifications, spare_parts
  )
  
  app.include_router(anomalib.router, prefix="/api/anomalib", tags=["Anomalib"])
  app.include_router(novavision.router, prefix="/api/novavision", tags=["NovaVision"])
  app.include_router(embeddings.router, prefix="/api/embeddings", tags=["Embeddings"])
  app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
  app.include_router(search.router, prefix="/api/search", tags=["Search"])
  app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
  app.include_router(spare_parts.router, prefix="/api/spare-parts", tags=["Spare Parts"])
  ```
  - Route çakışma kontrolü
  - Tag gruplaması (Swagger UI organizasyonu)
- **UAT:** `GET /openapi.json` tüm endpoint'leri listeliyor

#### Task 2.2: Health check endpoint
- **Files:** `server/routers/health.py`
- **Description:**
  - `GET /health` — tüm servislerin durumu:
    ```json
    {
      "status": "healthy",
      "services": {
        "supabase": "connected",
        "novavision": "running|stopped|mock",
        "puqai": "connected|offline",
        "llm": "configured|missing_key",
        "models": { "jina_clip": "loaded|not_loaded", "patchcore": "loaded|not_loaded" }
      },
      "version": "1.0.0",
      "uptime": 3600
    }
    ```
  - Lightweight: DB query yok, sadece bağlantı durumu
  - `GET /health/deep` — detaylı: DB query, model inference test (ağır, opsiyonel)
- **UAT:** `/health` < 50ms, tüm servis durumları doğru

### Wave 3: Hata Yönetimi & Logging

#### Task 3.1: Global exception handler
- **Files:** `server/middleware/error_handler.py`
- **Description:**
  - Tüm yakalanmamış exception'lar için global handler
  - Structured error response:
    ```json
    {
      "error": {
        "code": "INFERENCE_FAILED",
        "message": "NovaVision inference failed: timeout",
        "details": {"model_id": "..."},
        "timestamp": "2026-05-16T10:30:00Z"
      }
    }
    ```
  - HTTP exception'ları: 400, 404, 422, 500
  - Custom exception sınıfları: `SupabaseError`, `NovaVisionError`, `PUQAIError`, `ModelNotLoadedError`
- **UAT:** Hatalı istekte structured JSON error dönüyor

#### Task 3.2: Structured logging
- **Files:** `server/logging_config.py`
- **Description:**
  - Python `logging` modülü yapılandırması
  - JSON formatlı log (ELK/CloudWatch uyumlu)
  - Log seviyeleri: DEBUG, INFO, WARNING, ERROR
  - Request ID: her isteğe unique ID, log'da takip edilebilir
  - Supabase log tablosuna da yaz (opsiyonel, config'den)
  - Log rotation: günlük, 7 gün sakla
- **UAT:** Tüm endpoint istekleri request ID ile log'lanıyor

### Wave 4: CORS, Test & Dokümantasyon

#### Task 4.1: CORS yapılandırması
- **Files:** `server/main.py`
- **Description:**
  - Frontend için CORS middleware:
    ```python
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,  # ["http://localhost:3000", "tauri://localhost"]
        allow_methods=["*"],
        allow_headers=["*"],
    )
    ```
  - Production'da allow_origins kısıtlaması
- **UAT:** Frontend'den (localhost:3000) API çağrısı CORS hatası vermez

#### Task 4.2: Entegrasyon testleri
- **Files:** `tests/test_integration.py`
- **Description:**
  - E2E test: veri → embedding → inference → bildirim zinciri
  - Mock modda tüm servislerin birlikte çalıştığını doğrula
  - Test senaryoları:
    1. Görüntü yükle → embedding al → benzer görüntü ara
    2. Anomali tespit et → bildirim tetikle → webhook log'una yaz
    3. Soru sor → RAG pipeline → streaming yanıt al
    4. Kriz skoru hesapla → PO oluştur → alternatif tedarikçi bul
  - `pytest` + `httpx.AsyncClient` + `TestClient`
- **UAT:** Tüm entegrasyon testleri geçiyor

#### Task 4.3: OpenAPI dokümantasyonu
- **Files:** `server/main.py` (docstrings)
- **Description:**
  - Tüm endpoint'ler için docstring: summary, description, response model
  - FastAPI otomatik OpenAPI spec: `GET /openapi.json`
  - Swagger UI: `GET /docs`
  - ReDoc: `GET /redoc`
  - Custom description, tags, examples
  - Frontend geliştirici için: `/openapi.json` endpoint'i not et
- **UAT:** Swagger UI'da tüm endpoint'ler açıklamalı, "Try it out" çalışıyor

#### Task 4.4: Dependency güncelleme
- **Files:** `server/requirements.txt`, `server/pyproject.toml`
- **Description:**
  - Tüm bağımlılıkları güncelle:
    - fastapi, uvicorn, httpx, supabase-py
    - anomalib, torch, transformers, Pillow
    - google-generativeai, anthropic
    - pydantic-settings, python-dotenv
    - pytest, pytest-asyncio (dev)
  - Versiyon pin'leme
  - `pip install -r requirements.txt` tek komutta kurulum
- **UAT:** Temiz venv'de `pip install -r requirements.txt` hatasız

---

## Verification

- [ ] `uvicorn server.main:app` başlatılıyor, startup log'ları temiz
- [ ] `GET /health` tüm servis durumlarını doğru gösteriyor
- [ ] `GET /openapi.json` frontend için hazır
- [ ] `GET /docs` Swagger UI tüm endpoint'leri gösteriyor
- [ ] Entegrasyon testleri geçiyor (mock modda)
- [ ] CORS frontend'den erişime izin veriyor
- [ ] Graceful shutdown: CTRL+C ile temiz kapanma
- [ ] `.env` validasyonu eksik değişkende anlamlı hata

## must_haves

1. **FastAPI lifespan çalışıyor** — startup/shutdown yönetimi
2. **Tüm router'lar bağlı** — `/openapi.json` eksiksiz
3. **`/openapi.json` frontend için erişilebilir** — Arkadaşın frontend'i bununla yapacak
4. **Entegrasyon testleri geçiyor** — Tüm servisler birlikte çalışıyor
5. **Production-ready config** — `.env` validasyonu, CORS, logging

## Deliverables
- `server/main.py` (final — tüm router'lar bağlı, lifespan)
- `server/lifespan.py` + `server/config.py`
- `server/middleware/error_handler.py`
- `server/logging_config.py`
- `server/routers/health.py`
- `tests/test_integration.py`
- `server/requirements.txt` (güncel)
- `GET /openapi.json` → Frontend geliştirici için hazır
