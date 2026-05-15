# Yefai — Predictive Maintenance Platform

> Kestirimci bakım (predictive maintenance) için multimodal AI destekli masaüstü platformu.
> Gerçek zamanlı anomali tespiti, RAG tabanlı asistan, çok kanallı bildirim.

---

## What This Is

Yefai, üretim hatlarındaki takım aşınmasını (tool wear) gerçek zamanlı izleyen, 
anomali tespit eden ve operatörleri anında bilgilendiren bir **B2B masaüstü uygulamasıdır**.

**Core loop:** Sensör verisi + kamera görüntüsü → AI anomali tespiti → Dashboard uyarısı → Çok kanallı bildirim (Telegram, E-posta, SMS, Web)

**Farkı:** Zero-shot AI modelleri (TimesFM 2.5, Anomalib) ile eğitim gerektirmeden çalışır. 
RAG tabanlı chatbot ile geçmiş veriler, ürün detayları ve görseller üzerinden sorgulama yapılabilir.

## Core Value

> Operatör, makine arızalanmadan ÖNCE hangi takımın ne zaman değişmesi gerektiğini bilir.

- **Anlık anomali tespiti:** Sensör ve kamera verisinden saniyeler içinde anomali skoru
- **Sıfır eğitim (Zero-shot):** TimesFM 2.5 ve Anomalib ile model eğitmeden çalışır
- **Çok modlu (Multimodal):** Görüntü + zaman serisi + akustik + kuvvet verisi tek platformda
- **Akıllı asistan:** RAG ile veri seti üzerinde doğal dil sorgulama, görsel gösterme
- **Her yerden bildirim:** Telegram, e-posta, SMS, web bildirim

## Current State

- [x] MATWI veri seti indirildi (17 set, 1663 etiketli görüntü + sensör verisi)
- [x] FastAPI backend scaffold (`server/main.py`)
- [x] Next.js client scaffold (`client/`)
- [x] Multimodal yaklaşım dokümanı (`docs/Multimodal-Veri-Setleri-ve-Yaklaşımları.md`)
- [x] PUQ AI incelemesi (`server/docs/puqai-inceleme.md`)
- [ ] Veri seti ayıklanmadı (17 zip dosyası)
- [ ] Train/test split yapılmadı
- [ ] Tauri entegrasyonu yok (şu an Next.js)
- [ ] PostgreSQL + pgvector kurulmadı
- [ ] AI modelleri entegre edilmedi
- [ ] Bildirim sistemi yok

## Tech Stack

| Katman | Teknoloji | Açıklama |
|--------|-----------|----------|
| **Desktop Shell** | Tauri v2 | Rust tabanlı, hafif, cross-platform masaüstü uygulaması |
| **Frontend** | Next.js 16 + React | Tauri WebView içinde çalışacak |
| **Backend** | FastAPI (Python 3.11+) | AI inference, veri işleme, API gateway |
| **Database** | PostgreSQL 16 + pgvector | Vektör embedding'leri, ilişkisel veri, zaman serisi |
| **AI - Zaman Serisi** | Google TimesFM 2.5 | Zero-shot zaman serisi anomali tespiti |
| **AI - Görüntü** | Anomalib (PatchCore) | Zero-shot görüntü anomali tespiti |
| **AI - Embedding** | CLIP / SigLIP | Multimodal embedding (görüntü + metin) |
| **AI - LLM** | Gemini / Claude API | RAG chatbot, analiz, raporlama |
| **Streaming** | WebSocket + SSE | Gerçek zamanlı veri akışı |
| **Bildirim** | Telegram Bot, SMTP, Twilio | Çok kanallı alerting |
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
│  │ Inference│ │ RAG      │ │ Notification   │  │
│  │ Engine   │ │ Pipeline │ │ Service        │  │
│  └──────────┘ └──────────┘ └────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │         PostgreSQL + pgvector             │  │
│  │  Metadata │ Embeddings │ Time Series     │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Key Decisions

| Karar | Gerekçe | Sonuç |
|--------|---------|-------|
| Tauri yerine Electron? | Daha hafif, Rust güvenliği, daha az bellek | Tauri v2 |
| Next.js SPA olarak | Tauri WebView ile uyumlu, SSR gerekmez | `output: "export"` |
| Zero-shot AI (eğitimsiz) | Hackathon/demo için hızlı, eğitim döngüsü yok | TimesFM + Anomalib |
| pgvector vs Pinecone | Yerel çalışma, ek servis maliyeti yok, PostgreSQL zaten var | pgvector |
| CLIP vs özel embedding | Hazır multimodal model, sıfır kurulum | CLIP (OpenCLIP) |
| WebSocket vs polling | Gerçek zamanlı dashboard için gerekli | WebSocket + SSE fallback |

## Requirements

### Validated
(Henüz yok — implementasyonla doğrulanacak)

### Active
- [ ] **R1:** Gerçek zamanlı sensör verisi akışı ve dashboard'da canlı grafik
- [ ] **R2:** Multimodal anomali tespiti (görüntü + sensör füzyonu)
- [ ] **R3:** Anomali durumunda Telegram/E-posta/SMS/Web bildirimi
- [ ] **R4:** RAG tabanlı chatbot — veri seti üzerinde soru-cevap
- [ ] **R5:** Chatbot yanıtlarında tıklanabilir ürün görselleri ve tablo verileri
- [ ] **R6:** Streaming agent — anomali tespitinde otonom aksiyon
- [ ] **R7:** PostgreSQL pgvector ile multimodal embedding saklama ve arama
- [ ] **R8:** Tauri ile native dosya sistemi erişimi ve yerel bildirimler
- [ ] **R9:** Train/test split — test verisi üzerinde canlı demo
- [ ] **R10:** Anomali kaynağı tespiti (seri numarası, takım ID, zaman damgası)

### Out of Scope
- Model eğitimi (fine-tuning) — demo zero-shot çalışacak
- Multi-tenant bulut deployment — lokal masaüstü uygulaması
- Mobil uygulama — sadece masaüstü
- PUQ AI entegrasyonu — workflow otomasyonu ayrı proje

## Evolution

Bu doküman faz geçişlerinde ve milestone sınırlarında güncellenir.

- **Her faz sonrası:** Gereksinimler güncellenir, çıkarılanlar Out of Scope'a taşınır
- **Her milestone sonrası:** Tüm bölümler gözden geçirilir, Core Value kontrol edilir

---

*Last updated: 2026-05-15 — GSD initialization*
