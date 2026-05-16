---
phase: 2.5
slug: gelecek-tahmini
status: draft
created: 2026-05-16
sources:
  - .planning/PROJECT.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
  - .planning/research/tech-decisions.md
  - .planning/phases/02c-gelecek-tahmini/PLAN.md
---

# Phase 2.5 — Research Notes: Gelecek Tahmini (Wear Prediction Engine)

> Bu dosya rastgele doldurulmadı; mevcut GSD artifact’larından sentezlenmiştir. Yeni dış araştırma yapılmadıysa iddialar proje dokümanlarıyla sınırlıdır.

## Objective
Phase 2.5 planını doğru uygulamak için bilinmesi gereken kararlar, riskler ve doğrulama noktaları.

## Requirement Coverage
FR-8.1, FR-8.3, NFR-3

## Source-Backed Findings
- Skor→µm kalibrasyonu labels.csv gerçek wear değerleriyle doğrulanacak.
- Kritik eşik v1.0 planında 200 µm olarak kabul edildi.
- Phase 3B kriz skorunun lead-time karşılaştırması bu endpoint’i tüketecek.

## Manual Gate / Prerequisites
- Phase 2A anomalib skorları ve Phase 1 metadata hazır olmalı.

## Implementation Notes
- PLAN.md içindeki wave/task sırası canonical kabul edilir.
- Kapsam, ROADMAP.md’deki v1.0 backend sınırıyla sınırlıdır; frontend/Tauri/dashboard işleri bu fazın deliverable’ı değildir.
- Secret/API key içeren `.env` değerleri dokümana veya loglara yazılmamalıdır.

## Known Pitfalls
- Anomalib score ile gerçek wear lineer olmayabilir; MAE/RMSE raporlanmalı.
- 3’ten az zaman noktası olan setlerde confidence low/yetersiz veri dönmeli.
- hours_to_critical negatif veya sonsuz edge-case’leri explicit ele alınmalı.

## Open Questions / Decisions Needed
- Manual gate tamamlandı mı? Tamamlanmadıysa faz execution başlatılmamalı.
- Gerçek servis veya model gerektiren kontroller CI’da mock/marker ile ayrılacak mı?
- Performance hedefleri yerel makineye göre güncellenecek mi, yoksa PLAN.md’deki hedefler aynen mi korunacak?

## Validation Architecture
- Kalibrasyon MAE < 30µm hedefi test edilmeli.
- Scenario ordering optimistic > baseline > pessimistic olmalı.
- API response kriz servisi için stable interface sağlamalı.
- Migration constraints confidence değerlerini kısıtlamalı.

### Test Infrastructure Recommendation
- Framework: pytest + scipy/numpy unit tests
- Quick command: `pytest tests/phase02c -q`
- Full command: `pytest tests/phase02c tests/integration -q`
- Feedback latency target: < 60s

### Nyquist Sampling Policy
- Her task tamamlandığında ilgili automated command çalıştırılmalı.
- Her wave sonunda phase quick suite çalıştırılmalı.
- Faz kapanmadan önce full suite ve manual gate kontrolleri yeşil olmalı.
