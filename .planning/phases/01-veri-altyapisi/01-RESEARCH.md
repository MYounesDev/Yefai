---
phase: 1
slug: veri-altyapisi
status: draft
created: 2026-05-16
sources:
  - .planning/PROJECT.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - .planning/research/tech-decisions.md
  - .planning/phases/01-veri-altyapisi/PLAN.md
---

# Phase 1 — Research Notes: Veri Altyapısı & Supabase Setup

> Bu dosya rastgele doldurulmadı; mevcut GSD artifact’larından sentezlenmiştir. Yeni dış araştırma yapılmadıysa iddialar proje dokümanlarıyla sınırlıdır.

## Objective
Phase 1 planını doğru uygulamak için bilinmesi gereken kararlar, riskler ve doğrulama noktaları.

## Requirement Coverage
FR-1.1, FR-1.2, FR-1.3, FR-1.4, FR-1.5, FR-7.1, FR-7.2, FR-7.7

## Source-Backed Findings
- MATWI: 17 set, 1663 etiketli görüntü, 5 sensör kanalı; sync sorunu bekleniyor.
- Supabase sadece metadata + pgvector için kullanılacak; görüntü/sensör dosyaları local diskte kalacak.
- Mock spare-parts katmanı MATWI’de gerçek BOM/stok olmadığı için v1.0 demo verisi olarak üretilecek.

## Manual Gate / Prerequisites
- G1 — Supabase projesi, pgvector ve .env bağlantı bilgileri insan tarafından tamamlanmalı.

## Implementation Notes
- PLAN.md içindeki wave/task sırası canonical kabul edilir.
- Kapsam, ROADMAP.md’deki v1.0 backend sınırıyla sınırlıdır; frontend/Tauri/dashboard işleri bu fazın deliverable’ı değildir.
- Secret/API key içeren `.env` değerleri dokümana veya loglara yazılmamalıdır.

## Known Pitfalls
- Aynı set train ve test’e bölünürse leakage oluşur; split set bazlı olmalı.
- Görüntü BLOB veya sensör ham verisini Supabase’e yüklemek free-tier ve mimari kararı ihlal eder.
- Mock stok verisi gerçek veri gibi sunulmamalı; raporda sentetik olduğu açık yazılmalı.

## Open Questions / Decisions Needed
- Manual gate tamamlandı mı? Tamamlanmadıysa faz execution başlatılmamalı.
- Gerçek servis veya model gerektiren kontroller CI’da mock/marker ile ayrılacak mı?
- Performance hedefleri yerel makineye göre güncellenecek mi, yoksa PLAN.md’deki hedefler aynen mi korunacak?

## Validation Architecture
- Ayıklanan görüntü sayısı labels.csv ile eşleşmeli.
- Train/test split leakage kontrolü otomatik olmalı.
- Migration sonrası pgvector sütunu ve HNSW index doğrulanmalı.
- Mock kriz senaryoları en az crisis/at_risk örnekleri üretmeli.
- FastAPI /health endpoint’i çalışmalı.

### Test Infrastructure Recommendation
- Framework: pytest (Wave 0 installs; repo’da henüz test altyapısı yok)
- Quick command: `pytest tests/phase01 -q`
- Full command: `pytest tests/phase01 tests/integration -q`
- Feedback latency target: < 60s hedef

### Nyquist Sampling Policy
- Her task tamamlandığında ilgili automated command çalıştırılmalı.
- Her wave sonunda phase quick suite çalıştırılmalı.
- Faz kapanmadan önce full suite ve manual gate kontrolleri yeşil olmalı.
