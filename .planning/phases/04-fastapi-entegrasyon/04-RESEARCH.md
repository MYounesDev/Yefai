---
phase: 4
slug: fastapi-entegrasyon
status: draft
created: 2026-05-16
sources:
  - .planning/PROJECT.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - .planning/research/tech-decisions.md
  - .planning/phases/04-fastapi-entegrasyon/PLAN.md
---

# Phase 4 — Research Notes: FastAPI Lifespan & Entegrasyon

> Bu dosya rastgele doldurulmadı; mevcut GSD artifact’larından sentezlenmiştir. Yeni dış araştırma yapılmadıysa iddialar proje dokümanlarıyla sınırlıdır.

## Objective
Phase 4 planını doğru uygulamak için bilinmesi gereken kararlar, riskler ve doğrulama noktaları.

## Requirement Coverage
NFR-7, NFR-8, FR-2.2, FR-4.4, FR-5.3, FR-8.3

## Source-Backed Findings
- Tüm router’lar tek FastAPI app altında birleşecek.
- Health endpoint servis durumlarını lightweight dönecek; /health/deep ağır kontroller için opsiyonel.
- Frontend için /openapi.json ana contract olacak.

## Manual Gate / Prerequisites
- Phase 2A, 2B, 3A, 3B deliverable’ları ve .env değişkenleri hazır olmalı.

## Implementation Notes
- PLAN.md içindeki wave/task sırası canonical kabul edilir.
- Kapsam, ROADMAP.md’deki v1.0 backend sınırıyla sınırlıdır; frontend/Tauri/dashboard işleri bu fazın deliverable’ı değildir.
- Secret/API key içeren `.env` değerleri dokümana veya loglara yazılmamalıdır.

## Known Pitfalls
- Startup’ta tüm ağır modelleri eager load etmek dev deneyimini bozabilir; lazy loading kararı korunmalı.
- CORS production allowlist gevşek bırakılmamalı.
- Global exception handler secrets veya payload dump etmemeli.
- Integration testleri external servisleri mock modda çalıştırmalı.

## Open Questions / Decisions Needed
- Manual gate tamamlandı mı? Tamamlanmadıysa faz execution başlatılmamalı.
- Gerçek servis veya model gerektiren kontroller CI’da mock/marker ile ayrılacak mı?
- Performance hedefleri yerel makineye göre güncellenecek mi, yoksa PLAN.md’deki hedefler aynen mi korunacak?

## Validation Architecture
- /health <50ms ve servis status contract’ı test edilmeli.
- /openapi.json tüm router taglerini içermeli.
- E2E mock zinciri veri→embedding→inference→bildirim ve kriz→PO akışını doğrulamalı.
- Temiz venv dependency install UAT olarak manual/CI’da koşmalı.

### Test Infrastructure Recommendation
- Framework: pytest + pytest-asyncio + FastAPI TestClient/httpx
- Quick command: `pytest tests/phase04 -q`
- Full command: `pytest tests/phase04 tests/test_integration.py -q`
- Feedback latency target: < 120s mock

### Nyquist Sampling Policy
- Her task tamamlandığında ilgili automated command çalıştırılmalı.
- Her wave sonunda phase quick suite çalıştırılmalı.
- Faz kapanmadan önce full suite ve manual gate kontrolleri yeşil olmalı.
