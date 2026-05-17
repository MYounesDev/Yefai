# Yefai Agent Rules — Index

Bu klasör `.planning/` altındaki Yefai v1.0 planlarından türetilmiş zorunlu ajan kurallarını içerir.

## Önce oku
1. `01-scope-and-phase-gates.md` — kapsam, faz sırası, insan/manual gate kuralları
2. `02-data-storage-and-supabase.md` — veri yerleşimi, Supabase ve pgvector sınırları
3. `03-dataset-split-and-image-modeling.md` — MATWI, split, image model eğitimi
4. `04-ai-services-and-models.md` — Anomalib, Jina CLIP v2, NovaVision, RAG/LLM, PUQ AI
5. `05-mock-spare-parts-crisis.md` — yedek parça krizi mock/simülasyon kuralları
6. `06-api-fastapi-integration.md` — FastAPI endpoint, lifecycle, health, logging kuralları
7. `07-validation-and-testing.md` — test, mock/live ayrımı, kabul kriterleri
8. `08-documentation-and-change-control.md` — dokümantasyon, rapor ve değişiklik kuralları

## Genel öncelik sırası
1. `.planning/PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md` kararları bağlayıcıdır.
2. Faz özelindeki `PLAN.md`, `*-RESEARCH.md`, `*-VALIDATION.md` dosyaları faz içinde bağlayıcıdır.
3. Çelişki varsa kapsamı daraltan, mock/live ayrımını netleştiren ve veri sızıntısını önleyen kural kazanır.
4. Emin olunmayan dış servis/API davranışları için gerçek entegrasyon iddiası yazma; mock/skeleton ve net hata mesajı kullan.
5. **Paket yöneticisi olarak `uv` kullanılır** (`pip` değil).
6. **Her commit öncesi kalite gate:** `ruff check` → `ruff format --check` → `mypy` → `pytest` (bkz. `.pre-commit-config.yaml`)
7. **Commit mesajları conventional commit formatında** (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`)

## Kaynak plan dosyaları
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/research/tech-decisions.md`
- `.planning/image-model-training-plan.md`
- `.planning/gelecek-tahmini-plani.md`
- `.planning/yedek-parca-krizi-mock-plan.md`
- `.planning/phases/*/{PLAN.md,*-RESEARCH.md,*-VALIDATION.md}`
