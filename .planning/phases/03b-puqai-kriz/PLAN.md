---
phase: 3B
name: "PUQ AI Bildirim & Yedek Parça Krizi Otomasyonu"
goal: "PUQ AI webhook client, çok kanallı bildirim (Telegram/E-posta/SMS), yedek parça krizi skoru, otomatik PO, alternatif tedarikçi."
depends_on: "Phase 2B (inference pipeline), Phase 1 (mock yedek parça verisi)"
estimated_effort: "1.5 hafta"
manual_gate: "G3 — PUQ AI hesabı + workflow webhook URL'leri .env'de olmalı"
parallel: true
parallel_with: "Phase 3A"
assignee: "Kişi B"
---

# Plan: Phase 3B — PUQ AI Bildirim & Yedek Parça Krizi Otomasyonu

## Goal
Anomali tespitinde PUQ AI webhook tetikle, Telegram/E-posta/SMS bildirimleri gönder. Yedek parça krizi skoru hesapla, otomatik PO oluştur, alternatif tedarikçi öner. Webhook retry + log mekanizması.

## Prerequisites (Manual Gate)
- [ ] **G3:** PUQ AI hesabı oluşturuldu
- [ ] PUQ AI workflow'ları hazır: Telegram, E-posta, SMS (her biri için webhook URL al)
- [ ] `PUQAI_ANOMALY_WEBHOOK`, `PUQAI_EMAIL_WEBHOOK`, `PUQAI_SMS_WEBHOOK` `.env` dosyasında
- [ ] Test mesajı gönderilip alındığı doğrulandı

> **ÖNEMLİ — PUQ AI vs Kod Sorumluluk Ayrımı:**
> - **PUQ AI panelinde yapılacak:** Telegram bot bağlama, E-posta SMTP ayarları, SMS gateway entegrasyonu, alıcı listeleri, mesaj format şablonları. Tüm kanal konfigürasyonu puq.ai dashboard'undan yönetilir.
> - **Kodda yapılacak:** Sadece webhook URL'lerine POST isteği atmak. Payload (anomali detayı, skor, görüntü URL'i) kod tarafında hazırlanır, iletim PUQ AI tarafından yapılır.
> - Yani Telegram/E-posta/SMS gönderimi için herhangi bir Telegram Bot API, SMTP client, SMS gateway SDK'sı **yazılmaz**. Tek bağımlılık `httpx` ile webhook POST.

---

## Tasks

### Wave 1: PUQ AI Webhook Client

#### Task 1.1: PUQ AI webhook client
- **Files:** `server/ai/puqai/client.py`, `server/ai/puqai/schemas.py`
- **Description:**
  - `httpx.AsyncClient` ile async HTTP client — sadece webhook URL'lerine POST atar, kanal entegrasyonu PUQ AI panelinde yapılır
  - Webhook payload formatı:
    ```json
    {
      "event": "anomaly_detected",
      "timestamp": "2026-05-16T10:30:00Z",
      "machine": "MATWI-Tool-15mm",
      "anomaly": {
        "image_id": 42,
        "score": 0.87,
        "wear_type": "flank",
        "wear_value_um": 120.5,
        "set_id": 5
      },
      "image_url": "https://...",
      "severity": "critical"
    }
    ```
  - Async endpoint kullan (fire-and-forget, yanıt beklenmez)
  - 3 farklı webhook URL'si: anomaly, email, sms
- **UAT:** Mock webhook URL'sine POST atılıyor, 200 dönüyor

#### Task 1.2: Payload template'leri
- **Files:** `server/ai/puqai/templates/`
- **Description:**
  - **Anomaly Alert (Telegram):** Kısa format — seri no, skor, tip, zaman, thumbnail URL
  - **Detaylı Rapor (E-posta):** Tüm detaylar + görüntü eki (base64 veya URL)
  - **Kritik Uyarı (SMS):** 160 karakter limitli — "ANOMALI: Set5 Takim42 FlankWear 120um"
  - **Yedek Parça Krizi:** Parça adı, stok, lead time, kriz skoru, alternatif tedarikçi
  - **PO Bildirimi:** "Satin alma siparisi hazir - PartX, SupplierY, 450TL, onay bekliyor"
  - Jinja2 template engine ile dinamik doldurma
- **UAT:** Her template için örnek payload render edildi, format doğru

#### Task 1.3: Webhook retry + log
- **Files:** `server/ai/puqai/retry.py`, `server/db/migrations/002_webhook_logs.sql`
- **Description:**
  - Retry mekanizması: 3 retry, exponential backoff (1s, 4s, 16s)
  - Başarısız olursa `webhook_logs` tablosuna yaz
  - Supabase `webhook_logs` tablosu: id, event_type, payload, status, attempt, error, created_at
  - Retry queue: başarısız webhook'ları periyodik tekrar dene (5 dk'da bir)
  - Dashboard için log sorgulama endpoint'i
- **UAT:** 3 retry sonrası başarısız webhook log'da görünüyor

### Wave 2: Bildirim Servisi

#### Task 2.1: Bildirim tetikleme servisi
- **Files:** `server/services/notification_service.py`
- **Description:**
  - Anomali tespit edildiğinde otomatik tetikleme
  - Severity-based routing:
    - `score > 0.9` → SMS + Telegram + E-posta (kritik)
    - `score > 0.7` → Telegram + E-posta (uyarı)
    - `score > 0.5` → Sadece E-posta (bilgi)
  - Batch notification: çoklu anomali için tek mesaj
  - Notification throttle: aynı image için 5 dk içinde tekrar gönderme
- **UAT:** Anomali skoruna göre doğru kanallara bildirim gidiyor

#### Task 2.2: PUQ AI offline fallback
- **Files:** `server/ai/puqai/fallback.py`
- **Description:**
  - PUQ AI offline ise → OS native notification (macOS: `osascript`)
  - Log'a yaz: hangi bildirimler kaçırıldı
  - PUQ AI geri gelince backlog'daki bildirimleri gönder
  - Config: `PUQAI_FALLBACK_ENABLED=true/false`
- **UAT:** PUQ AI URL'si yanlışsa OS notification gösteriliyor

### Wave 3: Yedek Parça Krizi Otomasyonu

#### Task 3.1: Kriz skoru hesaplama
- **Files:** `server/services/crisis_service.py`
- **Description:**
  - Anomali tespit edilen görüntü → ilgili parçayı eşleştir (mock catalog'dan)
  - Kriz skoru (0-100) hesaplama:
    - Stok açığı: mevcut stok / ihtiyaç (ağırlık: %30)
    - Lead time farkı: (supplier lead time) - (anomaliye kadar süre) (ağırlık: %25)
    - Kritiklik: A/B/C sınıfı parça (ağırlık: %20)
    - Supplier riski: güvenilirlik skoru tersi (ağırlık: %15)
    - Anomali şiddeti: anomaly_score ile orantılı (ağırlık: %10)
  - Risk seviyesi: none (<20), watch (20-40), at_risk (40-70), crisis (>70)
- **UAT:** Her risk seviyesi için en az 1 örnek senaryo, skor formülü tutarlı

#### Task 3.2: Otomatik PO oluşturma
- **Files:** `server/services/purchase_order_service.py`
- **Description:**
  - Kriz (`crisis` veya `at_risk`) durumunda otomatik mock PO oluştur
  - PO fields: part_id, supplier_id, quantity, unit_price, total, lead_time_days, status, created_at
  - Status akışı: `draft` → `ready_for_review` → `approved` (manuel simüle) / `cancelled`
  - Supabase `purchase_orders` tablosuna yaz
  - Aynı parça için duplicate PO önleme (son 24 saat)
- **UAT:** Kriz durumunda PO otomatik oluşuyor, `ready_for_review` durumunda

#### Task 3.3: Alternatif tedarikçi tarama
- **Files:** `server/services/supplier_service.py`
- **Description:**
  - Birincil tedarikçi lead time'ı kritik eşiğe yetişmezse alternatif ara
  - Alternatif skorlama: lead time, maliyet farkı, güvenilirlik
  - Alternatif öneri response: supplier list + karşılaştırma (lead time, maliyet %, güvenilirlik)
  - Tek tedarikçili parça: "alternatif yok" uyarısı
- **UAT:** Lead time yetişmeyen senaryoda alternatif supplier dönüyor

### Wave 4: FastAPI Endpoint'leri

#### Task 4.1: Notification router
- **Files:** `server/routers/notifications.py`
- **Description:**
  - `POST /api/notifications/anomaly` — anomali bildirimi tetikle (body: anomaly_id)
  - `POST /api/notifications/report` — rapor bildirimi (body: report_type, parameters)
  - `GET /api/notifications/logs?event_type=&status=&limit=` — webhook log'ları
  - `GET /api/notifications/status` — PUQ AI bağlantı durumu
- **UAT:** Swagger UI'da bildirim tetiklenebiliyor

#### Task 4.2: Spare parts router
- **Files:** `server/routers/spare_parts.py`
- **Description:**
  - `GET /api/spare-parts/catalog` — parça kataloğu
  - `GET /api/spare-parts/crisis-score/{image_id}` — kriz skoru hesapla
  - `POST /api/spare-parts/auto-order` — otomatik PO oluştur
  - `GET /api/spare-parts/alternative-suppliers/{part_id}` — alternatif tedarikçi öner
  - `GET /api/spare-parts/inventory` — stok durumu
  - `GET /api/spare-parts/purchase-orders?status=` — PO listesi
- **UAT:** Tüm endpoint'ler mock veri ile çalışıyor

---

## Verification

- [ ] PUQ AI webhook 3 kanala da (Telegram, E-posta, SMS) gönderim yapıyor
- [ ] Retry mekanizması: 3 deneme, başarısız log'a yaz
- [ ] Severity-based routing doğru kanallara yönleniyor
- [ ] Kriz skoru formülü tüm senaryolarda tutarlı (0-100)
- [ ] Otomatik PO `ready_for_review` durumunda oluşuyor
- [ ] Alternatif tedarikçi önerisi lead time + maliyet karşılaştırmalı
- [ ] Fallback OS notification çalışıyor

## must_haves

1. **PUQ AI webhook 3 kanal** — Telegram, E-posta, SMS çalışır durumda
2. **Webhook retry + log** — Bildirim kaybı olmaması için
3. **Kriz skoru hesaplama** — 0-100 arası tutarlı skor
4. **Otomatik PO** — Kriz durumunda müdahalesiz PO oluşumu
5. **Fallback mekanizması** — PUQ AI offline olsa bile sistem uyarı verir

## Deliverables
- `server/ai/puqai/client.py` + `schemas.py` + `templates/`
- `server/ai/puqai/retry.py` + `fallback.py`
- `server/services/notification_service.py`
- `server/services/crisis_service.py` + `purchase_order_service.py` + `supplier_service.py`
- `server/routers/notifications.py` + `server/routers/spare_parts.py`
- `server/db/migrations/002_webhook_logs.sql`
