# Yefai — Predictive Maintenance Platform

> Kestirimci bakım (predictive maintenance) için multimodal AI destekli masaüstü platformu.
> Gerçek zamanlı anomali tespiti, RAG tabanlı asistan, çok kanallı bildirim.

---

## What This Is

Yefai, üretim hatlarındaki takım aşınmasını (tool wear) gerçek zamanlı izleyen, 
anomali tespit eden ve operatörleri anında bilgilendiren bir **B2B masaüstü uygulamasıdır**.

**Core loop:** Sensör verisi + kamera görüntüsü → AI anomali tespiti → Dashboard uyarısı → yedek parça stok krizi kontrolü → otomatik PO + alternatif tedarikçi önerme → FastAPI webhook → PUQ AI → Çok kanallı bildirim (Telegram, E-posta, SMS, Web)

**Farkı:** Zero-shot AI modelleri (TimesFM 2.5, Anomalib) ile eğitim gerektirmeden çalışır. 
RAG tabanlı chatbot ile geçmiş veriler, ürün detayları ve görseller üzerinden sorgulama yapılabilir.

## Core Value

> Operatör, makine arızalanmadan ÖNCE hangi takımın ne zaman değişmesi gerektiğini bilir.

- **Anlık anomali tespiti:** Sensör ve kamera verisinden saniyeler içinde anomali skoru
- **Sıfır eğitim (Zero-shot):** TimesFM 2.5 ve Anomalib ile model eğitmeden çalışır
- **Çok modlu (Multimodal):** Görüntü + zaman serisi + akustik + kuvvet verisi tek platformda
- **Yedek parça krizi simülasyonu:** Anomali/tahmin çıktısını mock stok, lead time, otomatik PO ve alternatif tedarikçi önerme ile birleştirir
- **Akıllı asistan:** RAG ile veri seti üzerinde doğal dil sorgulama, görsel gösterme
- **Her yerden bildirim:** Telegram, e-posta, SMS, web bildirim

## v1.0 Scope — İki Aşamalı

### Aşama 1: AI Backend (BU FAZLAR) ✅ Aktif
Backend odaklı: AI pipeline, FastAPI, Supabase. **Frontend yok.**
7 faz, 2 kişi paralel çalışabilir. Detay: `ROADMAP.md`

### Aşama 2: Frontend + Desktop (SONRA)
Next.js dashboard, Tauri desktop shell, WebSocket streaming. Backend hazır olunca başlar.

## Current State

- [x] MATWI veri seti indirildi (17 set, 1663 etiketli görüntü + sensör verisi)
- [x] FastAPI backend scaffold (`server/main.py`)
- [x] Next.js client scaffold (`client/`) — frontend aşaması için
- [x] Multimodal yaklaşım dokümanı (`docs/Multimodal-Veri-Setleri-ve-Yaklaşımları.md`)
- [x] PUQ AI incelemesi (`server/docs/puqai-inceleme.md`)
- [x] MATWI'de gerçek stok/BOM verisi olmadığı tespit edildi; yedek parça krizi için mock plan eklendi (`.planning/yedek-parca-krizi-mock-plan.md`)
- [x] ROADMAP.md paralel 7-phase yapıya güncellendi (2026-05-16)
- [x] G1: Supabase projesi oluşturuldu — Yefai `jgufisddsdmappcnglcf`; REST HTTP 200, DB connect OK
- [~] G2: NovaVision local gate kısmi — `docker --version` ve `novavision --help` çalışıyor; token/local install/container/live model doğrulaması bekliyor
- [ ] G3: PUQ AI hesabı + webhook URL'leri alınmadı
- [ ] G4: LLM API key alınmadı
- [x] Veri seti ayıklandı/parse edildi (17 set; Phase 1 summary: 1803 labeled images)
- [x] Train/test split yapıldı — set-bazlı, leakage yok (1292 train / 511 test)
- [x] Mock yedek parça kataloğu, envanter snapshot'ı, ticket datası ve mock PO üretildi
- [x] Supabase + pgvector kuruldu — `vector` extension 0.8.0 doğrulandı
- [~] AI modelleri — Phase 2B NovaVision mock-mode API contract entegre edildi; Phase 2A model artifact ve live NovaVision deploy/inference bekliyor
- [ ] Bildirim sistemi yok

Durum göstergesi: `[x]` tamamlandı, `[ ]` başlamadı, `[~]` kısmi/mock veya manual gate bekliyor.

## Tech Stack

| Katman | Teknoloji | Açıklama |
|--------|-----------|----------|
| **Desktop Shell** | Tauri v2 | Rust tabanlı, hafif, cross-platform masaüstü uygulaması |
| **Frontend** | Next.js 16 + React | Tauri WebView içinde çalışacak |
| **Backend** | FastAPI (Python 3.11+) | AI inference, veri işleme, API gateway |
| **Database** | Supabase pgvector (metadata + vektör) + Local disk (görüntü + sensör) | Embedding vektörleri cloud'da, ağır dosyalar local'de. Hibrit. |
| **AI - Görüntü Anomali (Train)** | Anomalib (PatchCore) | Few-shot görüntü anomali tespiti, lokal eğitim |
| **AI - Görüntü Anomali (Inference)** | NovaVision CLI (local Docker) | Lokal eğitilen Torch modeli NovaVision CLI ile local Docker container'a deploy edilir, inference localhost'ta |
| **AI - Embedding** | Jina CLIP v2 (865M) | Görüntü + metin aynı vektör uzayında, 89 dil (Türkçe), lokal, MRL |
| **AI - LLM** | Gemini / Claude API | RAG chatbot, analiz, raporlama |
| **Streaming** | WebSocket + SSE | Gerçek zamanlı veri akışı |
| **Bildirim & Otomasyon** | PUQ AI | Webhook tetiklemeli, Telegram/E-posta/SMS workflow'ları |
| **Agent** | Hermes Agent SDK | Otonom AI ajan iş akışları |

## Architecture (High-Level)

```
┌─────────────────────────────────────────────────┐
│                  Tauri Desktop                    │
│  ┌───────────────────────────────────────────┐  │
│  │          Next.js Frontend (WebView)        │  │
│  │  Dashboard │ Chatbot │ Alerts │ Settings   │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │           Tauri Rust Backend               │  │
│  │  FS Access │ Native Notifications │ IPC   │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Server                       │
│  ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ Inference│ │ RAG      │ │ PUQ AI         │  │
│  │ Engine   │ │ Pipeline │ │ Webhook Client │  │
│  └──────────┘ └──────────┘ └───────┬────────┘  │
│                                     │            │
└─────────────────────────────────────┼────────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │      PUQ AI          │
                           │  Telegram │ Email    │
                           │  SMS │ Slack │ Web   │
                           └─────────────────────┘
│  ┌──────────────────────────────────────────┐  │
│  │         Supabase + pgvector               │  │
│  │  Metadata │ Embeddings │ Time Series     │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Key Decisions

| Karar | Gerekçe | Sonuç |
|--------|---------|-------|
| Tauri yerine Electron? | Daha hafif, Rust güvenliği, daha az bellek | Tauri v2 |
| Next.js SPA olarak | Tauri WebView ile uyumlu, SSR gerekmez | `output: "export"` |
| Few-shot görüntü anomali (Anomalib) | Hackathon/demo için hızlı, az train örneği yeterli | Anomalib PatchCore |
| Supabase vs PostgreSQL | Managed pgvector, built-in auth, dashboard, row-level security | Supabase |
| pgvector vs Pinecone | Supabase'de built-in, ek servis maliyeti yok | pgvector |
| Jina CLIP v2 (tek embedding modeli) | Görüntü+metin aynı uzayda, 89 dil, lokal, EmbeddingGemma+Gemini API'yi tek modelde birleştirir | Jina CLIP v2 (865M, 1024-dim, MRL) |
| Yedek parça krizi | MATWI'de stok/BOM/lead time verisi yok; demo için otomatik PO + alternatif tedarikçi simülasyonu | Mock inventory + suppliers + ticket + PO katmanı; gerçek ERP v1.1+ |
| Bildirim: kendimiz vs PUQ AI | Zorunlu entegrasyon, webhook ile tetiklenen workflow | PUQ AI (Telegram/E-posta/SMS) |
| WebSocket vs polling | Gerçek zamanlı dashboard için gerekli | WebSocket + SSE fallback |

## Requirements

### Validated
(Henüz yok — implementasyonla doğrulanacak)

### Active
- [ ] **R1:** Gerçek zamanlı sensör verisi akışı ve dashboard'da canlı grafik
- [ ] **R2:** Görüntü tabanlı anomali tespiti (Anomalib PatchCore)
- [ ] **R3:** Anomali durumunda FastAPI → PUQ AI webhook → Telegram/E-posta/SMS bildirimi
- [ ] **R4:** RAG tabanlı chatbot — veri seti üzerinde soru-cevap
- [ ] **R5:** Chatbot yanıtlarında tıklanabilir ürün görselleri ve tablo verileri
- [ ] **R6:** Streaming agent — anomali tespitinde otonom aksiyon zinciri (PUQ AI workflow tetikleme)
- [ ] **R7:** Supabase pgvector ile görüntü embedding saklama ve arama (Jina CLIP v2, 1024-dim)
- [ ] **R8:** Tauri ile native dosya sistemi erişimi ve yerel bildirimler
- [ ] **R9:** Train/test split (%70/%30) — test verisi üzerinde canlı demo
- [ ] **R10:** Anomali kaynağı tespiti (seri numarası, takım ID, zaman damgası, aşınma tipi)
- [ ] **R11:** PUQ AI workflow'ları: anomali alert, periyodik rapor, kritik durum escalasyonu
- [ ] **R12:** Yedek parça krizi mock katmanı: sentetik parça kataloğu, tedarikçi listesi, stok snapshot'ı, lead time, ticket, otomatik PO ve alternatif tedarikçi önerme, kriz skoru

### Out of Scope
- Sensör tabanlı anomali tespiti (TimesFM) — v1.1+ için ertelendi
- Model fine-tuning — demo zero/few-shot çalışacak
- Multi-tenant bulut deployment — lokal masaüstü uygulaması
- Mobil uygulama — sadece masaüstü
- Gerçek ERP/MRO/CMMS entegrasyonu (gerçek stok, gerçek satın alma PO execute) — v1.0'da mock/simülasyon, gerçek entegrasyon v1.1+
- Dinamik stok optimizasyonu (reorder point auto-adjust) — v1.1+
- Gerçek tedarikçi veritabanı entegrasyonu — v1.0'da mock supplier listesi, gerçek entegrasyon v1.1+

> **v1.0 kapsamında:** Otomatik mock sipariş (PO hazırlama → satın alma ekranı → manuel onay), alternatif tedarikçi önerme (mock supplier verisiyle). Gerçek satın alma işlemi yapılmaz.

## Evolution

Bu doküman faz geçişlerinde ve milestone sınırlarında güncellenir.

- **Her faz sonrası:** Gereksinimler güncellenir, çıkarılanlar Out of Scope'a taşınır
- **Her milestone sonrası:** Tüm bölümler gözden geçirilir, Core Value kontrol edilir
- **v1.0 Backend fazları:** ROADMAP.md'deki 7 faz, Phase 1→2A∥2B→2.5∥3A∥3B→4 akışı

---

*Last updated: 2026-05-16 — Phase 2B mock-mode NovaVision API contract durumu ve 7 fazlı backend akışı işlendi*
