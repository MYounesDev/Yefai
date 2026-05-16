---
phase: 3A
slug: rag-pipeline
status: draft
created: 2026-05-16
sources:
  - .planning/PROJECT.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - .planning/research/tech-decisions.md
  - .planning/phases/03a-rag-pipeline/PLAN.md
---

# Phase 3A — Research Notes: RAG Pipeline

> Bu dosya rastgele doldurulmadı; mevcut GSD artifact’larından sentezlenmiştir. Yeni dış araştırma yapılmadıysa iddialar proje dokümanlarıyla sınırlıdır.

## Objective
Phase 3A planını doğru uygulamak için bilinmesi gereken kararlar, riskler ve doğrulama noktaları.

## Requirement Coverage
FR-4.1, FR-4.4, FR-4.5, FR-7.5, NFR-3, NFR-6

## Source-Backed Findings
- RAG: soru → Jina CLIP v2 text embedding → pgvector top-k → metadata/context → LLM streaming.
- Türkçe prompt varsayılan; provider Gemini veya Claude olarak config’den seçilecek.
- Frontend yok; SSE API ve search endpoint’leri üretilecek.

## Manual Gate / Prerequisites
- G4 — LLM API key ve provider .env’de olmalı; Phase 2A embedding’leri hazır olmalı.

## Implementation Notes
- PLAN.md içindeki wave/task sırası canonical kabul edilir.
- Kapsam, ROADMAP.md’deki v1.0 backend sınırıyla sınırlıdır; frontend/Tauri/dashboard işleri bu fazın deliverable’ı değildir.
- Secret/API key içeren `.env` değerleri dokümana veya loglara yazılmamalıdır.

## Known Pitfalls
- LLM context’e base64 görüntü eklemek token bütçesini patlatabilir; context assembly limitli olmalı.
- Embedding yoksa metadata fallback açıkça test edilmeli.
- Session memory kullanıcılar arası sızıntı yapmamalı.
- Rate limit ve streaming errors structured döndürülmeli.

## Open Questions / Decisions Needed
- Manual gate tamamlandı mı? Tamamlanmadıysa faz execution başlatılmamalı.
- Gerçek servis veya model gerektiren kontroller CI’da mock/marker ile ayrılacak mı?
- Performance hedefleri yerel makineye göre güncellenecek mi, yoksa PLAN.md’deki hedefler aynen mi korunacak?

## Validation Architecture
- Provider abstraction mock ile streaming test edilmeli.
- Hybrid search filtreli/filtersiz sonuçları doğrulanmalı.
- SSE curl/httpx ile test edilmeli.
- 10 örnek Türkçe soru için beklenen metadata kaynakları kontrol edilmeli.

### Test Infrastructure Recommendation
- Framework: pytest + pytest-asyncio; LLM live testleri mock dışı marker
- Quick command: `pytest tests/phase03a -q -m "not live"`
- Full command: `pytest tests/phase03a -q`
- Feedback latency target: < 90s mock

### Nyquist Sampling Policy
- Her task tamamlandığında ilgili automated command çalıştırılmalı.
- Her wave sonunda phase quick suite çalıştırılmalı.
- Faz kapanmadan önce full suite ve manual gate kontrolleri yeşil olmalı.
