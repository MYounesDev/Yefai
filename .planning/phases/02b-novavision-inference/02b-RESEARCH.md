---
phase: 2B
slug: novavision-inference
status: draft
created: 2026-05-16
sources:
  - .planning/PROJECT.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - .planning/research/tech-decisions.md
  - .planning/phases/02b-novavision-inference/PLAN.md
---

# Phase 2B — Research Notes: NovaVision Local Inference Pipeline

> Bu dosya rastgele doldurulmadı; mevcut GSD artifact’larından sentezlenmiştir. Yeni dış araştırma yapılmadıysa iddialar proje dokümanlarıyla sınırlıdır.

## Objective
Phase 2B planını doğru uygulamak için bilinmesi gereken kararlar, riskler ve doğrulama noktaları.

## Requirement Coverage
FR-2.2, FR-2.3, FR-5.2

## Source-Backed Findings
- NovaVision v1.0’da local Docker inference için kullanılacak; bulut inference yok.
- Model .pt Phase 2A’dan gelene kadar mock mode ile endpoint ve lifecycle geliştirilebilir.
- Sonuçlar Supabase anomalies tablosuna yazılacak.

## Manual Gate / Prerequisites
- G2 — Docker Desktop, novavision CLI, NovaVision token ve local install insan tarafından tamamlanmalı.

## Implementation Notes
- PLAN.md içindeki wave/task sırası canonical kabul edilir.
- Kapsam, ROADMAP.md’deki v1.0 backend sınırıyla sınırlıdır; frontend/Tauri/dashboard işleri bu fazın deliverable’ı değildir.
- Secret/API key içeren `.env` değerleri dokümana veya loglara yazılmamalıdır.

## Known Pitfalls
- Gerçek NovaVision CLI/API komutları public olmayabilir; wrapper mock ve hata mesajlarını izole etmeli.
- Container health check olmadan inference çağrısı flaky olur.
- Model beklerken phase bloklanmamalı; mock mode sözleşmesi Phase 4’e kadar korunmalı.

## Open Questions / Decisions Needed
- Manual gate tamamlandı mı? Tamamlanmadıysa faz execution başlatılmamalı.
- Gerçek servis veya model gerektiren kontroller CI’da mock/marker ile ayrılacak mı?
- Performance hedefleri yerel makineye göre güncellenecek mi, yoksa PLAN.md’deki hedefler aynen mi korunacak?

## Validation Architecture
- CLI wrapper subprocess hataları anlamlı exception’a çevirmeli.
- Mock mode tüm endpoint’leri gerçek model olmadan test ettirmeli.
- Lifecycle start/stop/restart davranışı idempotent olmalı.
- Gerçek model entegrasyon testi slow/live marker ile ayrılmalı.

### Test Infrastructure Recommendation
- Framework: pytest + pytest-asyncio; live Docker/NovaVision testleri marker ile ayrılır
- Quick command: `pytest tests/phase02b -q -m "not live"`
- Full command: `pytest tests/phase02b -q`
- Feedback latency target: < 90s mock; live değişken

### Nyquist Sampling Policy
- Her task tamamlandığında ilgili automated command çalıştırılmalı.
- Her wave sonunda phase quick suite çalıştırılmalı.
- Faz kapanmadan önce full suite ve manual gate kontrolleri yeşil olmalı.
