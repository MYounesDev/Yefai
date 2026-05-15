# Yefai — Predictive Maintenance Platform

> Kestirimci bakım (predictive maintenance) için multimodal AI destekli masaüstü platformu.
> Gerçek zamanlı anomali tespiti, RAG tabanlı asistan, çok kanallı bildirim.

---

## What This Is

Yefai, üretim hatlarındaki takım aşınmasını (tool wear) gerçek zamanlı izleyen, 
anomali tespit eden ve operatörleri anında bilgilendiren bir **B2B masaüstü uygulamasıdır**.

**Core loop:** Sensör verisi + kamera görüntüsü → AI anomali tespiti → Dashboard uyarısı → yedek parça stok krizi kontrolü → FastAPI webhook → PUQ AI → Çok kanallı bildirim (Telegram, E-posta, SMS, Web)

**Farkı:** Zero-shot AI modelleri (TimesFM 2.5, Anomalib) ile eğitim gerektirmeden çalışır. 
RAG tabanlı chatbot ile geçmiş veriler, ürün detayları ve görseller üzerinden sorgulama yapılabilir.

## Core Value

> Operatör, makine arızalanmadan ÖNCE hangi takımın ne zaman değişmesi gerektiğini bilir.

- **Anlık anomali tespiti:** Sensör ve kamera verisinden saniyeler içinde anomali skoru
- **Sıfır eğitim (Zero-shot):** TimesFM 2.5 ve Anomalib ile model eğitmeden çalışır
- **Çok modlu (Multimodal):** Görüntü + zaman serisi + akustik + kuvvet verisi tek platformda
- **Yedek parça krizi simülasyonu:** Anomali/tahmin çıktısını mock stok, lead time ve ticket verisiyle birleştirir
- **Akıllı asistan:** RAG ile veri seti üzerinde doğal dil sorgulama, görsel gösterme
- **Her yerden bildirim:** Telegram, e-posta, SMS, web bildirim

## Current State

- [x] MATWI veri seti indirildi (17 set, 1663 etiketli görüntü + sensör verisi)
- [x] FastAPI backend scaffold (`server/main.py`)
- [x] Next.js client scaffold (`client/`)
- [x] Multimodal yaklaşım dokümanı (`docs/Multimodal-Veri-Setleri-ve-Yaklaşımları.md`)
- [x] PUQ AI incelemesi (`server/docs/puqai-inceleme.md`)
- [x] MATWI'de gerçek stok/BOM verisi olmadığı tespit edildi; yedek parça krizi için mock plan eklendi (`.planning/yedek-parca-krizi-mock-plan.md`)
- [ ] Veri seti ayıklanmadı (17 zip dosyası)
- [ ] Train/test split yapılmadı
- [ ] Mock yedek parça kataloğu, envanter snapshot'ı ve ticket datası üretilmedi
- [ ] Tauri entegrasyonu yok (şu an Next.js)
- [ ] Supabase + pgvector kurulmadı
- [ ] AI modelleri entegre edilmedi
- [ ] Bildirim sistemi yok

## Tech Stack

| Katman | Teknoloji | Açıklama |
|--------|-----------|----------|
| **Desktop Shell** | Tauri v2 | Rust tabanlı, hafif, cross-platform masaüstü uygulaması |
| **Frontend** | Next.js 16 + React | Tauri WebView içinde çalışacak |
| **Backend** | FastAPI (Python 3.11+) | AI inference, veri işleme, API gateway |
| **Database** | Supabase + pgvector | Vektör embedding'leri, ilişkisel veri, managed PostgreSQL |
| **AI - Görüntü Anomali (Train)** | Anomalib (PatchCore) | Few-shot görüntü anomali tespiti, lokal eğitim |
| **AI - Görüntü Anomali (Inference)** | NovaVision | Lokal eğitilen Torch modeli NovaVision'a yüklenir, preprocessing + inference NovaVision'da |
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
| Yedek parça krizi | MATWI'de stok/BOM/lead time verisi yok; demo için gerçekmiş gibi label'a karıştırmak yanlış olur | Ayrı mock inventory + ticket katmanı |
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
- [ ] **R12:** Yedek parça krizi mock katmanı: sentetik parça kataloğu, stok snapshot'ı, lead time, ticket ve kriz skoru

### Out of Scope
- Sensör tabanlı anomali tespiti (TimesFM) — v1.1+ için ertelendi
- Model fine-tuning — demo zero/few-shot çalışacak
- Multi-tenant bulut deployment — lokal masaüstü uygulaması
- Mobil uygulama — sadece masaüstü
- Gerçek ERP/MRO/CMMS stok entegrasyonu — v1.0'da mock/simülasyon, gerçek entegrasyon v1.1+

## Evolution

Bu doküman faz geçişlerinde ve milestone sınırlarında güncellenir.

- **Her faz sonrası:** Gereksinimler güncellenir, çıkarılanlar Out of Scope'a taşınır
- **Her milestone sonrası:** Tüm bölümler gözden geçirilir, Core Value kontrol edilir

---

*Last updated: 2026-05-15 — GSD initialization*
