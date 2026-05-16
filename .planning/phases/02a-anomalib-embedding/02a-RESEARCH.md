---
phase: 2A
slug: anomalib-embedding
status: draft
created: 2026-05-16
sources:
  - .planning/PROJECT.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - .planning/research/tech-decisions.md
  - .planning/phases/02a-anomalib-embedding/PLAN.md
---

# Phase 2A — Research Notes: Anomalib Training & Embedding Pipeline

> Bu dosya rastgele doldurulmadı; mevcut GSD artifact’larından sentezlenmiştir. Yeni dış araştırma yapılmadıysa iddialar proje dokümanlarıyla sınırlıdır.

## Objective
Phase 2A planını doğru uygulamak için bilinmesi gereken kararlar, riskler ve doğrulama noktaları.

## Requirement Coverage
FR-2.1, FR-2.3, FR-2.4, FR-2.6, FR-7.2, FR-7.3, FR-7.5

## Source-Backed Findings
- Anomalib PatchCore few-shot yaklaşımı normal/düşük aşınmalı örneklerden memory bank kuracak.
- Jina CLIP v2 tek multimodal embedding modeli olarak seçildi; 1024 boyut pgvector hedefi.
- Phase 2B’nin gerçek entegrasyonu bu fazın .pt model export’una bağlı.

## Manual Gate / Prerequisites
- Phase 1 tamamlanmış olmalı; Jina CLIP v2 model erişimi ve Python bağımlılıkları hazır olmalı.

## Implementation Notes
- PLAN.md içindeki wave/task sırası canonical kabul edilir.
- Kapsam, ROADMAP.md’deki v1.0 backend sınırıyla sınırlıdır; frontend/Tauri/dashboard işleri bu fazın deliverable’ı değildir.
- Secret/API key içeren `.env` değerleri dokümana veya loglara yazılmamalıdır.

## Known Pitfalls
- Train setine anomalili/high-wear görüntü karışırsa PatchCore kalitesi bozulur.
- Jina CLIP v2 trust_remote_code ve model cache davranışı kontrollü yönetilmeli.
- Embedding boyutu schema ile uyuşmazsa pgvector insert/search kırılır.
- Aşınma tipi doğruluğu için labels.csv mapping’i test edilmeli.

## Open Questions / Decisions Needed
- Manual gate tamamlandı mı? Tamamlanmadıysa faz execution başlatılmamalı.
- Gerçek servis veya model gerektiren kontroller CI’da mock/marker ile ayrılacak mı?
- Performance hedefleri yerel makineye göre güncellenecek mi, yoksa PLAN.md’deki hedefler aynen mi korunacak?

## Validation Architecture
- Anomalib dataset klasör yapısı ve threshold analizi doğrulanmalı.
- PatchCore checkpoint ve .pt export load edilebilir olmalı.
- 1663 embedding üretimi ve pgvector araması test edilmeli.
- Swagger’da anomalib ve embedding endpoint’leri görünmeli.

### Test Infrastructure Recommendation
- Framework: pytest + pytest-asyncio (Wave 0)
- Quick command: `pytest tests/phase02a -q`
- Full command: `pytest tests/phase02a tests/integration -q`
- Feedback latency target: < 120s mock/smoke; full model testleri opsiyonel slow marker

### Nyquist Sampling Policy
- Her task tamamlandığında ilgili automated command çalıştırılmalı.
- Her wave sonunda phase quick suite çalıştırılmalı.
- Faz kapanmadan önce full suite ve manual gate kontrolleri yeşil olmalı.
