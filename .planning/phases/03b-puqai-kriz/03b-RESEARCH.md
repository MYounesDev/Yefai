---
phase: 3B
slug: puqai-kriz
status: draft
created: 2026-05-16
sources:
  - .planning/PROJECT.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - .planning/research/tech-decisions.md
  - .planning/phases/03b-puqai-kriz/PLAN.md
---

# Phase 3B — Research Notes: PUQ AI Bildirim & Yedek Parça Krizi Otomasyonu

> Bu dosya rastgele doldurulmadı; mevcut GSD artifact’larından sentezlenmiştir. Yeni dış araştırma yapılmadıysa iddialar proje dokümanlarıyla sınırlıdır.

## Objective
Phase 3B planını doğru uygulamak için bilinmesi gereken kararlar, riskler ve doğrulama noktaları.

## Requirement Coverage
FR-5.3, FR-5.4, FR-5.5, FR-5.6, FR-5.8, FR-8.1, FR-8.3, FR-8.6, FR-8.7, FR-8.8

## Source-Backed Findings
- Bildirimler PUQ AI webhook ile tetiklenecek; retry ve webhook_logs tablosu zorunlu.
- Kriz skoru stok açığı, lead time, kritiklik, supplier riski ve anomali şiddetinden oluşacak.
- Auto-PO mock/simülasyon; gerçek satın alma işlemi yok.

## Manual Gate / Prerequisites
- G3 — PUQ AI hesabı, workflow webhook URL’leri ve test mesajları insan tarafından doğrulanmalı.

## Implementation Notes
- PLAN.md içindeki wave/task sırası canonical kabul edilir.
- Kapsam, ROADMAP.md’deki v1.0 backend sınırıyla sınırlıdır; frontend/Tauri/dashboard işleri bu fazın deliverable’ı değildir.
- Secret/API key içeren `.env` değerleri dokümana veya loglara yazılmamalıdır.

## Known Pitfalls
- Webhook URL/secrets loglarda sızdırılmamalı.
- Fire-and-forget bildirimde başarısızlık sessiz kaybolmamalı; retry + log şart.
- Duplicate PO önleme olmazsa kriz senaryosu spam üretir.
- OS notification fallback platform bağımlı; CI’da mocklanmalı.

## Open Questions / Decisions Needed
- Manual gate tamamlandı mı? Tamamlanmadıysa faz execution başlatılmamalı.
- Gerçek servis veya model gerektiren kontroller CI’da mock/marker ile ayrılacak mı?
- Performance hedefleri yerel makineye göre güncellenecek mi, yoksa PLAN.md’deki hedefler aynen mi korunacak?

## Validation Architecture
- Webhook client mock server’a 200/500 senaryolarıyla test edilmeli.
- Retry 1s/4s/16s policy davranışı fake timer ile doğrulanmalı.
- Kriz skoru tüm risk seviyeleri için örnek üretmeli.
- Auto-order duplicate guard ve supplier fallback test edilmeli.

### Test Infrastructure Recommendation
- Framework: pytest + pytest-asyncio + respx/httpx mock
- Quick command: `pytest tests/phase03b -q`
- Full command: `pytest tests/phase03b tests/integration -q`
- Feedback latency target: < 90s

### Nyquist Sampling Policy
- Her task tamamlandığında ilgili automated command çalıştırılmalı.
- Her wave sonunda phase quick suite çalıştırılmalı.
- Faz kapanmadan önce full suite ve manual gate kontrolleri yeşil olmalı.
