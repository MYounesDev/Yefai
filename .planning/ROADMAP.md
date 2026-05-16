# Roadmap — Yefai Predictive Maintenance Platform

> Yüksek seviye faz yapısı. Her faz bağımsız olarak planlanır (`/gsd-plan-phase N`).
> **v1.0 Backend kapsamı:** Sadece AI pipeline + FastAPI + Supabase. Frontend (Next.js, Tauri, Dashboard UI) bu fazların dışındadır.

---

## Milestone: Yefai v1.0 — AI Backend

**Hedef:** MATWI veri seti üzerinde Anomalib PatchCore ile görüntü anomali tespiti, NovaVision inference, Jina CLIP v2 embedding, pgvector hibrit arama, RAG chatbot API'si, PUQ AI bildirim otomasyonu, yedek parça krizi simülasyonu.

**Kapsam dışı:** Frontend (Next.js dashboard UI, Tauri desktop shell, WebSocket streaming)

**Zaman hedefi:** 4.5-5 hafta (part-time, 2 kişi paralel)
**Granularity:** Medium (7 faz)
**Paralel yapı:** Phase 2A∥2B ve Phase 3A∥3B∥2.5 aynı anda farklı kişilerce yürütülebilir.

---

## ⚠️ MANUAL GATES (Fazlardan Önce İnsan Tarafından Yapılması Gerekenler)

Bu işlemler otomatik değildir. İlgili faz başlamadan önce tamamlanmış olmalıdır.

| Gate ID | Açıklama | Gerekli Faz | Nasıl Yapılır |
|---------|----------|-------------|---------------|
| **G1** | ✅ TAMAMLANDI — Supabase projesi oluştur + pgvector aktifleştir + connection string al | Phase 1 | Yefai `jgufisddsdmappcnglcf`; `.env` hazır; REST HTTP 200; DB connect OK; `vector` 0.8.0 doğrulandı |
| **G2** | ⚠️ KISMİ — Docker ve NovaVision CLI komutları çalışıyor; token/local install/live container doğrulanmadı | Phase 2B | Kalan: novavision.ai'den token al, `novavision install local <TOKEN>` çalıştır, `.env` içine `NOVAVISION_TOKEN`, `NOVAVISION_MOCK=false`, `NOVAVISION_INFERENCE_URL` ekle, Phase 2A `.pt` artifact ile live testleri çalıştır |
| **G3** | PUQ AI hesabı oluştur + workflow webhook URL'lerini al | Phase 3B | puq.ai → Register → Workflow oluştur (Telegram, E-posta, SMS trigger) → Her workflow için webhook URL'sini `.env` dosyasına `PUQAI_ANOMALY_WEBHOOK`, `PUQAI_EMAIL_WEBHOOK`, `PUQAI_SMS_WEBHOOK` olarak kaydet |
| **G4** | Gemini / Claude API key al | Phase 3A | aistudio.google.com veya console.anthropic.com → API key → `.env` dosyasına `LLM_API_KEY` ve `LLM_PROVIDER` (gemini/claude) olarak kaydet |

> **ÖNEMLİ:** Fazlar başlamadan önce ilgili gate'lerin tamamlandığını `.env` dosyasını kontrol ederek doğrula. Gate tamamlanmamışsa faz başlatılmaz.

---

## Phase 1: Veri Altyapısı & Supabase Setup

**Amaç:** MATWI veri setini local'e ayıkla, Supabase'e SADECE metadata + embedding vektörleri için şema kur, mock yedek parça verisini üret. Görüntü ve sensör dosyaları local diskte kalır.

**Kim yapar:** İki kişi birlikte (tek faz, bölünemez)

**Kapsam:**
- 17 zip dosyasını `data/MATWI/Set*/` altına local'e ayıkla
- labels.csv ve sets.csv'den metadata çıkar
- Sensör CSV'lerini parse et (Accelerometer, Acoustic, Force X/Y/Z) — **local'de kalır**
- Train/test split (%70/%30) — set bazında, aynı set asla bölünmez
- **Supabase şeması (hafif):** `sets`, `images` (metadata + `image_embedding vector(1024)` + `file_path` — local path), `anomalies` tabloları. **Görüntü dosyası Supabase'e yüklenmez.**
- pgvector embedding sütunu: `image_embedding vector(1024)` + HNSW index. **Sadece vektörler (~7MB) cloud'da.**
- **Mock yedek parça katmanı:** `spare_parts_catalog`, `suppliers`, `inventory_snapshots`, `part_tickets`, `purchase_orders` — **local CSV + Supabase tabloları** (veri küçük, ikisi de)
- Veri kalite raporu: kaç eşleşen görüntü-sensör çifti, eksik/bozuk veri
- Mock yedek parça kalite raporu
- **FastAPI proje yapısı:** `server/` altında router, model, service, config
- Supabase Python client bağlantısı (`supabase-py`) + local dosya sistemi erişimi

**Mimari karar:** Görüntüler (~330MB) ve sensör CSV'leri (~50MB) local diskte. Supabase sadece metadata + embedding vektörleri (~10MB) tutar. Free plan limitine takılmaz. FastAPI `/api/images/{id}` endpoint'i local diskten serve eder.

**Bağımlılıklar:** G1 (Supabase projesi + pgvector aktif olmalı)
**Deliverable:** Local veri seti, Supabase'de hafif şema + metadata, veri kalite raporu, FastAPI iskeleti
**Tahmini süre:** 1.5 hafta

---

## Phase 2A: Anomalib Training & Embedding Pipeline ∥

**Amaç:** Anomalib PatchCore ile görüntü anomali modeli eğit, Jina CLIP v2 ile embedding üret, pgvector'e yaz.

**Kim yapar:** Kişi A (Phase 2B ile paralel çalışır)

**Kapsam:**
- Anomalib Python API ile PatchCore eğitimi:
  - Normal/düşük aşınmalı train görüntülerinden memory bank oluştur
  - `coreset_sampling_ratio=0.1`, `backbone="wide_resnet50_2"`
  - Torch modeli `.pt` olarak export et (Phase 2B için)
- Test setinde anomali skoru hesaplama (lokal inference)
- Aşınma tipi sınıflandırması: Flank wear, Adhesive wear, Combination
- Jina CLIP v2 embedding pipeline:
  - Model indirme ve cache'leme (`jinaai/jina-clip-v2`, trust_remote_code=True)
  - 1663 görüntü için batch embedding (< 20sn hedef)
  - MRL ile opsiyonel boyut kısaltma (1024 → 64/128/256)
- Toplu embedding → Supabase pgvector yazma
- FastAPI endpoint'leri:
  - `POST /api/anomalib/train` — eğitim başlatma
  - `GET /api/anomalib/status/{job_id}` — eğitim durumu
  - `POST /api/anomalib/predict` — lokal inference
  - `POST /api/embeddings/generate` — embedding üretme
  - `GET /api/embeddings/search?q=...&top_k=5` — vektör arama

**Bağımlılıklar:** Phase 1 (veri + Supabase)
**Deliverable:** Eğitilmiş PatchCore modeli (.pt), embedding'ler pgvector'de, FastAPI endpoint'leri
**Tahmini süre:** 2 hafta

---

## Phase 2B: NovaVision Local Inference Pipeline ∥

**Amaç:** Phase 2A'da eğitilen Torch modelini NovaVision CLI ile local Docker container'a deploy et, localhost inference pipeline'ını kur. **Tamamen local — bulut API yok.**

**Kim yapar:** Kişi B (Phase 2A ile paralel, model .pt dosyası hazır olana kadar mock/skeleton ile çalışır)

**Kapsam:**
- **NovaVision CLI wrapper (`novavision` komutu):** install, start server, deploy app, start/stop app
- **Docker container yönetimi:** container lifecycle (startup/shutdown/health check), crash recovery
- **Model deploy:** Phase 2A'dan gelen .pt modelini app olarak container'a yükle, model versiyonlama
- **Local inference:** localhost REST API üzerinden preprocessing + inference, sonuçları Supabase'e yaz
- NovaVision offline fallback GEREKMEZ — zaten local, container düşerse Phase 2A lokal inference'a yönlenir
- FastAPI endpoint'leri:
  - `POST /api/novavision/deploy` — model deploy
  - `GET /api/novavision/models` — deploy edilmiş modeller
  - `POST /api/novavision/inference` — inference başlatma
  - `GET /api/novavision/inference/{job_id}` — sonuç sorgulama
  - `GET /api/novavision/health` — container durumu

**NOT:** Phase 2A'dan model .pt dosyası gelene kadar:
- Docker + NovaVision CLI kurulumu ve container ayağa kaldırma yapılır
- Mock response ile inference endpoint'leri yazılır
- Gerçek model hazır olduğunda sadece deploy + test (2 saatlik iş)

**Bağımlılıklar:** Phase 1, G2 (Docker + NovaVision CLI + token), Phase 2A (model .pt — son entegrasyon)
**Deliverable:** Local Docker container'da çalışan NovaVision inference, FastAPI endpoint'leri
**Tahmini süre:** 1.5 hafta (model beklerken mock ile çalışır, model gelince 2 günde entegre olur)

**Durum — 2026-05-16:** Mock-mode NovaVision backend contract uygulandı ve test edildi. Wrapper/service/router ayrımı, `/api/novavision/*` endpointleri, ana `/health` NovaVision özeti, mock-mode API testleri ve live/manual-gate test skeleton'ı mevcut. G2 token/local install/container ve Phase 2A `.pt` artifact olmadığı için live deploy/inference tamamlandı diye işaretlenmedi. Detay: `.planning/phases/02b-novavision-inference/SUMMARY.md` ve `reports/novavision_phase02b.md`.

---

## Phase 2.5: Gelecek Tahmini (Wear Prediction Engine)

**Amaç:** Anomalib skorlarından aşınma seviyesi tahmini, lineer regresyon ile aşınma hızı hesaplama, kritik eşiğe kalan süre, 3 senaryolu projeksiyon. Backend-only: veriyi üret, API'den sun.

**Kim yapar:** Kişi B (Phase 2B bittikten sonra, Phase 3B'den önce)

**Kapsam:**
- Anomalib skor (0-1) → aşınma seviyesi (µm) kalibrasyonu
- Lineer regresyon ile aşınma hızı hesaplama (µm/saat)
- Kritik eşiğe (200 µm) kalan süre projeksiyonu
- 3 senaryo: mevcut hız (baseline), hızlanırsa (+%25), yavaşlarsa (-%25)
- Aşınma trend analizi: accelerating / stable / decelerating
- Güven göstergesi: low / medium / high (r² ve veri noktası sayısına göre)
- `anomalies` tablosuna yeni kolonlar: `estimated_wear_um`, `wear_rate_um_per_hour`, `hours_to_critical`, `confidence`
- Phase 3B ile entegrasyon noktası: `hours_to_critical` vs lead time karşılaştırması
- FastAPI endpoint'leri:
  - `GET /api/predictions/{machine_id}` — detaylı tahmin
  - `GET /api/predictions/factory/overview` — tüm makineler özet
  - `POST /api/predictions/recalculate/{machine_id}` — yeniden hesapla

**Bağımlılıklar:** Phase 2A (anomali skorları Supabase'de hazır olmalı)
**Deliverable:** Aşınma tahmin API'si, 3 senaryolu projeksiyon verisi
**Tahmini süre:** 1 hafta

---

## Phase 3A: RAG Pipeline ∥

**Amaç:** pgvector + LLM ile doğal dil sorgulama yapabilen RAG chatbot API'si.

**Kim yapar:** Kişi A (Phase 2A bittikten sonra, Phase 3B ile paralel)

**Kapsam:**
- RAG pipeline:
  - Kullanıcı sorusu → Jina CLIP v2 metin embedding'i
  - pgvector cosine similarity search (top-k = 5)
  - Metadata filtreleme (set, wear seviyesi, tarih aralığı)
  - Context assembly (görüntü base64 + metadata + sensör verisi)
  - LLM'e context + sistem prompt + soru gönder
- LLM entegrasyonu:
  - Gemini Flash / Claude sonnet (`.env`'den provider seçimi)
  - Streaming response (SSE)
  - Token limit ve rate limit yönetimi
- Prompt template sistemi:
  - Sistem prompt'u: rol, veri seti bağlamı, yanıt formatı
  - Context template'i: görüntü + metadata formatı
  - Fallback: embedding yoksa sadece metadata ile yanıt
- Hibrit arama: vektör similarity + SQL metadata filtre (tek sorguda)
- Chat session yönetimi (Supabase'de session tablosu)
- FastAPI endpoint'leri:
  - `POST /api/chat` — soru sor, streaming SSE yanıt
  - `GET /api/chat/sessions` — session listesi
  - `GET /api/chat/sessions/{id}` — session geçmişi
  - `POST /api/search/hybrid` — hibrit arama (vektör + metadata)

**Bağımlılıklar:** Phase 2A (embedding'ler pgvector'de), G4 (LLM API key)
**Deliverable:** RAG chatbot API'si, streaming yanıt, hibrit arama
**Tahmini süre:** 1.5 hafta

---

## Phase 3B: PUQ AI Bildirim & Yedek Parça Krizi Otomasyonu ∥

**Amaç:** Anomali tespitinde PUQ AI webhook tetikleme, çok kanallı bildirim, yedek parça krizi otomasyonu (skor, PO, alternatif tedarikçi).

**Kim yapar:** Kişi B (Phase 2B bittikten sonra, Phase 3A ile paralel)

**Kapsam:**
- PUQ AI webhook client:
  - `httpx` async HTTP client
  - Webhook payload formatı: anomali detayları (seri no, skor, aşınma tipi, zaman, görüntü URL)
  - Async endpoint kullanımı (fire-and-forget)
  - Retry mekanizması: 3 retry, exponential backoff (1s, 4s, 16s)
  - Webhook log'ları Supabase `webhook_logs` tablosunda
- PUQ AI workflow'ları için payload şablonları:
  - **Anomali Alert (Telegram):** seri no, görüntü, skor, zaman, aşınma tipi
  - **Detaylı Rapor (E-posta):** tüm anomali detayları + görüntü eki
  - **Kritik Uyarı (SMS):** kısa mesaj (karakter limitli)
  - **Yedek Parça Krizi:** parça adı, stok, lead time, kriz skoru, alternatif tedarikçi
  - **PO Bildirimi:** "Satın alma siparişi hazır, onay bekliyor" + PO özeti
- **Yedek Parça Krizi Otomasyonu:**
  - Kriz skoru hesaplama: stok açığı, lead time farkı, kritiklik, supplier riski, anomali şiddeti → 0-100 skor + risk seviyesi
  - Otomatik PO oluşturma: kriz/anomalide uygun parça için mock purchase order
  - Alternatif tedarikçi tarama: lead time yetişmeyen durumda alternatif önerme
- Fallback: PUQ AI offline ise OS native notification + log
- FastAPI endpoint'leri:
  - `POST /api/notifications/anomaly` — anomali bildirimi tetikle
  - `POST /api/notifications/report` — rapor bildirimi tetikle
  - `GET /api/notifications/logs` — webhook log'ları
  - `GET /api/spare-parts/crisis-score/{image_id}` — kriz skoru hesapla
  - `POST /api/spare-parts/auto-order` — otomatik PO oluştur
  - `GET /api/spare-parts/alternative-suppliers/{part_id}` — alternatif tedarikçi öner

**Bağımlılıklar:** Phase 2B (inference), G3 (PUQ AI webhook URL'leri)
**Deliverable:** Çalışan bildirim sistemi, yedek parça krizi otomasyonu, FastAPI endpoint'leri
**Tahmini süre:** 1.5 hafta

---

## Phase 4: FastAPI Lifespan & Entegrasyon

**Amaç:** Tüm servisleri FastAPI lifespan altında birleştir, entegrasyon testlerini yap, production-ready hale getir.

**Kim yapar:** İki kişi birlikte (final entegrasyon)

**Kapsam:**
- FastAPI lifespan yönetimi:
  - `startup`: Supabase bağlantısı, model yükleme (Jina CLIP v2, Anomalib), config validasyonu
  - `shutdown`: Bağlantı kapatma, graceful shutdown
  - Environment variable validasyonu (`.env` kontrolü)
- Tüm router'ları `server/main.py` altında birleştir:
  - `/api/anomalib/*` — Phase 2A
  - `/api/novavision/*` — Phase 2B
  - `/api/embeddings/*` — Phase 2A
  - `/api/chat/*` — Phase 3A
  - `/api/search/*` — Phase 3A
  - `/api/notifications/*` — Phase 3B
  - `/api/spare-parts/*` — Phase 3B
- Health check: `GET /health` (DB, model, NovaVision, PUQ AI durumu)
- OpenAPI (Swagger) dokümantasyon: tüm endpoint'ler için
- CORS yapılandırması (frontend için)
- Entegrasyon testleri:
  - E2E: veri → embedding → inference → bildirim zinciri
  - Mock: NovaVision ve PUQ AI offline senaryoları
- Hata yönetimi: global exception handler, structured error response
- Logging: yapılandırılmış log (Supabase log tablosu + konsol)
- `requirements.txt` ve `pyproject.toml` güncelleme

**Bağımlılıklar:** Phase 3A, Phase 3B
**Deliverable:** Production-ready FastAPI sunucusu, OpenAPI dokümanı, entegrasyon testleri
**Tahmini süre:** 1 hafta

---

## Phase Order & Parallel Execution

```
MANUAL GATES (G1, G2, G3, G4) — önceden tamamlanmalı
          │
          ▼
     Phase 1 (Birlikte)
     Veri + Supabase
          │
     ┌────┴────────┐
     ▼              ▼
Phase 2A (Kişi A)   Phase 2B (Kişi B)       ← PARALEL
Anomalib+Embedding  NovaVision Local
     │              │
     │              ▼
     │         Phase 2.5 (Kişi B)           ← 2B bitince başlar
     │         Gelecek Tahmini
     │              │
     ▼              ▼
Phase 3A (Kişi A)   Phase 3B (Kişi B)       ← PARALEL
RAG Pipeline        PUQ AI + Kriz
     │              │
     └────┬─────────┘
          ▼
     Phase 4 (Birlikte)
     Lifespan + Entegrasyon
```

### Paralel Çalışma Kuralları

| Kural | Açıklama |
|-------|----------|
| **Phase 1 tek** | Veri altyapısı ortak, her ikisi de aynı fazda çalışır |
| **2A ∥ 2B** | Farklı kod alanları, aynı Supabase'e yazarlar. Merge conflict riski düşük. |
| **2.5 (Kişi B)** | Phase 2B bitince başlar. Phase 2A'daki skorları kullanır. Phase 3A ve 3B ile paralel yürüyebilir. |
| **3A ∥ 3B ∥ 2.5** | Farklı servisler, aynı anda geliştirilebilir. Sadece Phase 4'te birleşir. |
| **Phase anında bitir** | Bir faz tamamlanmadan diğerine geçilmez |
| **A kişisi path:** | Phase 1 → 2A → 3A → 4 |
| **B kişisi path:** | Phase 1 → 2B → 2.5 → 3B → 4 |

### Neden Bu Yapı?

- **Phase 2A ve 2B paralel:** Anomalib eğitimi (CPU/GPU yoğun, lokal) ile NovaVision Docker container (I/O yoğun, local) birbirini beklemez.
- **Phase 2.5 (Kişi B):** Phase 2B daha kısa (1.5 hafta), Kişi B erken bitirince 2.5'e başlar. Phase 2A'daki anomali skorlarını kullanır, Phase 3B'deki kriz skorunun ihtiyacı olan `hours_to_critical` verisini üretir.
- **Phase 3A, 3B ve 2.5 paralel:** RAG (LLM + embedding), bildirim otomasyonu (webhook + kriz) ve tahmin engine (regresyon + projeksiyon) farklı domain'ler.
- **Aynı kişi kendi fazlarını sıralı yapar:** Kişi A: 2A→3A, Kişi B: 2B→3B. Bağımlılık zinciri net.

---

## Teknik Borç & Sonraki Versiyonlar (v1.1+)

| Konu | Açıklama |
|------|----------|
| TimesFM sensör anomali tespiti | Sensör verisiyle prediction-based anomaly detection |
| Frontend integrasyonu | Next.js dashboard + Tauri desktop shell |
| Model fine-tuning | Anomalib ve TimesFM için kendi veri setimizle fine-tune |
| Gerçek kamera entegrasyonu | IP kamera / RTSP stream |
| Multi-instance | Aynı anda birden fazla makine izleme |
| Windows/Linux build | Cross-platform Tauri build |
| Kullanıcı yönetimi | Rol tabanlı erişim (operatör, yönetici, admin) |
| Gerçek ERP/MRO entegrasyonu | Mock → gerçek stok, satın alma, tedarikçi |

---

## Nasıl Başlanır?

```bash
# 1. ÖNCE manual gate'leri tamamla (G1, G2, G3, G4)
# 2. Phase 1 planını oluştur ve başlat:
/gsd-plan-phase 1

# 3. Phase 1 bittikten sonra paralel başlat:
# Kişi A (terminal 1): /gsd-plan-phase 2A
# Kişi B (terminal 2): /gsd-plan-phase 2B
# Phase 2B bitince: /gsd-plan-phase 2.5
```

---

*Last updated: 2026-05-16 — Phase 2B mock-mode NovaVision contract durumu ve G2 kalan işleri işlendi*
