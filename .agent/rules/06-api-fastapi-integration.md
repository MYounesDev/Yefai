# FastAPI API & Integration Rules

## Kesinlikle yapılacaklar
- FastAPI proje yapısını servis/router/config ayrımıyla kur.
- Startup/lifespan sırasında config validasyonu, Supabase bağlantısı ve gerekirse model lazy/eager yükleme stratejisini belirle.
- Shutdown sırasında bağlantıları ve model kaynaklarını düzgün kapat.
- Tüm faz routerlarını entegrasyon aşamasında `server/main.py` altında birleştir:
  - `/api/anomalib/*`
  - `/api/novavision/*`
  - `/api/embeddings/*`
  - `/api/chat/*`
  - `/api/search/*`
  - `/api/notifications/*`
  - `/api/spare-parts/*`
  - `/api/predictions/*` varsa Phase 2.5 için
- `GET /health` endpoint'i DB, model, NovaVision, PUQ AI/mock durumlarını raporlamalı.
- Structured error response ve global exception handler kullan.
- Structured logging yap; webhook ve önemli otomasyon olaylarını denetlenebilir şekilde logla.
- CORS ayarını frontend/Tauri aşaması için config'ten yönetilebilir tut (`localhost:3000`, `tauri://localhost` gibi origin'ler).
- OpenAPI/Swagger dokümantasyonunda tüm endpoint'leri görünür ve açıklamalı tut.
- Async dış çağrılarda `httpx.AsyncClient` gibi non-blocking client kullan.

## Kesinlikle yapılmayacaklar
- Router ve servis mantığını tek dosyada kontrolsüz büyütme.
- Environment değişkenleri eksik olduğunda sessizce yanlış live mode'a geçme.
- Mock mode ile live mode'u aynı status gibi gösterme; health ve loglarda açıkça ayır.
- NovaVision/PUQ AI/LLM gibi dış veya local-live servislerde hardcoded credential/token yazma.
- CORS'u güvenliksiz şekilde kalıcı `*` bırakma; geliştirme için kullanılsa bile config ile sınırla.
- Endpoint'i OpenAPI'de belgesiz veya response schema'sız bırakma.

## Beklenen önemli endpointler
- Anomalib: train, status, predict.
- Embedding/search: generate, vector/hybrid search.
- NovaVision: deploy, models, inference, inference status, health.
- RAG: chat streaming SSE, sessions, hybrid search.
- Notifications: anomaly, report, logs.
- Spare parts: crisis score, auto-order, alternative suppliers.
- Predictions: machine detail, factory overview, recalculate.
