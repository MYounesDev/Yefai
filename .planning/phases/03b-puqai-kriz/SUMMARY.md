---
phase: 3B
slug: puqai-kriz
status: implemented_mock_green
completed_at: 2026-05-17T03:37:44Z
scope: backend_mock_mode
---

# Phase 3B — Summary: PUQ AI Bildirim & Yedek Parça Krizi

## Sonuç

Phase 3B backend mock-mode kapsamı uygulandı: PUQ AI webhook istemcisi, payload template'leri, retry/fallback altyapısı, bildirim servisi, kriz skoru, otomatik mock PO, alternatif tedarikçi endpoint'leri ve tek çağrılık spare-parts crisis workflow endpoint'i mevcut.

G3 gerçek PUQ AI hesabı/webhook URL'leri manuel gate olduğu için live kanal gönderimi tamamlandı olarak işaretlenmedi; kod tarafı mock/test contract yeşil.

## Uygulanan Dosyalar

- `server/ai/puqai/client.py` — async webhook POST client
- `server/ai/puqai/config.py` — PUQ AI environment config
- `server/ai/puqai/fallback.py` — offline fallback davranışı
- `server/ai/puqai/retry.py` — 1s/4s/16s retry ve retry queue
- `server/ai/puqai/schemas.py` — webhook/payload/log şemaları
- `server/ai/puqai/template_engine.py` + `server/ai/puqai/templates/*.j2` — bildirim template'leri
- `server/services/notification_service.py` — severity-based notification routing + spare-parts crisis/PO helper
- `server/services/spare_parts_workflow_service.py` — prediction + crisis + PO + supplier + notification orchestration
- `server/services/crisis_service.py` — stok/lead time/kritiklik/supplier/anomali ağırlıklı kriz skoru
- `server/services/purchase_order_service.py` — mock PO oluşturma ve duplicate guard
- `server/services/supplier_service.py` — alternatif tedarikçi sıralama
- `server/routers/notifications.py` — notification/status/log API'leri
- `server/routers/spare_parts.py` — catalog, crisis-score, auto-order, alternatives, inventory, purchase-orders API'leri
- `tests/phase03b/*` — phase-specific unit/API tests

## Endpoint Contract

- `POST /api/notifications/anomaly`
- `POST /api/notifications/report`
- `GET /api/notifications/logs`
- `GET /api/notifications/status`
- `GET /api/spare-parts/catalog`
- `GET /api/spare-parts/crisis-score/{image_id}`
- `POST /api/spare-parts/auto-order`
- `GET /api/spare-parts/alternative-suppliers/{part_id}`
- `GET /api/spare-parts/inventory`
- `GET /api/spare-parts/purchase-orders`
- `GET /api/spare-parts/purchase-orders/{po_id}`
- `POST /api/spare-parts/crisis-workflow`

## Kabul Kriteri Durumu

- ✅ Mock spare-parts catalog, supplier, inventory ve purchase-order servisleri API'den erişilebilir.
- ✅ Kriz skoru 0-100 aralığında ve risk level `none/watch/at_risk/crisis` contract'ına bağlı.
- ✅ `at_risk` ve `crisis` PO ihtiyacı doğurur; PO `ready_for_review` durumunda mock oluşturulur.
- ✅ Alternatif tedarikçi endpoint'i lead time filtresiyle öneri döndürür.
- ✅ Birleşik `POST /api/spare-parts/crisis-workflow` endpoint'i prediction, crisis, purchase_order, alternative_suppliers ve notification bloklarını tek payload ile döndürür.
- ✅ PUQ AI payload template'lerinde yedek parça krizi ve PO bildirimi alanları var.
- ✅ Retry mekanizması 3 deneme ve exponential backoff contract'ı ile test edildi.
- ⚠️ Gerçek Telegram/E-posta/SMS gönderimi G3 manuel PUQ AI webhook gate'ine bağlıdır.
- ⚠️ Dashboard/RAG gösterimleri backend contract üzerinden sonraki frontend/RAG işleriyle bağlanacak; Phase 3B backend scope dışına taşırılmadı.

## Doğrulama

Son doğrulama 2026-05-17T03:37:44Z sonrası çalıştırıldı:

```bash
cd server
uv run pytest ../tests/phase03b -q
# 84 passed

uv run pre-commit run --all-files
# ruff, ruff-format, mypy, pytest passed
```

Manual API smoke:

```bash
POST /api/spare-parts/crisis-workflow
# HTTP 200; prediction/crisis/purchase_order/alternative_suppliers/notification blokları döndü
```

Graphify çıktısı da güncellendi:

```bash
graphify update .
graphify export obsidian
```
