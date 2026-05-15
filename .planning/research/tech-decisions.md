# Research Synthesis — Yefai Project

> Domain araştırması, teknoloji seçimleri, rakip/platform incelemeleri.
> Her bulgu PROJECT.md veya ROADMAP.md'deki bir kararı besler.

---

## 1. NovaVision AI

**URL:** https://novavision.ai/
**Tip:** No-code bilgisayar görüşü (computer vision) platformu

### Bulgular
- Kocaeli Teknopark / Londra merkezli Türk girişimi
- "Connect – Run – Action" framework: kamera bağla → CV workflow çalıştır → aksiyon al
- Hazır uygulamalar: Predictive Maintenance, PPE Detection, Object Counting, Crowd Analysis, Equipment Inspection vs.
- Platform modülleri: Collect → Annotate → Augment → Train → Build → Deploy → Connect → Monitor → Maintain → Secure
- **Embedding API'si YOK** — NovaVision bir embedding sağlayıcısı değil, uçtan uca CV platformu
- API dokümantasyonu herkese açık değil (demo talep etmek gerekiyor)

### Yefai için Değerlendirme
- **Doğrudan embedding için kullanılamaz** — CLIP/SigLIP gibi açık modeller kullanılacak
- **Potansiyel entegrasyon:** İleride görüntü işleme pipeline'ı olarak (v1.1+)
- **Alternatif embedding:** OpenCLIP (ViT-B/32), SigLIP, veya Jina CLIP v2
- NovaVision'ın "Predictive Maintenance" ve "Equipment Inspection" uygulamaları konsept olarak Yefai'ye benziyor — rakip değil, potansiyel iş birliği

---

## 2. Multimodal Embedding Yaklaşımları

### CLIP (OpenAI) / OpenCLIP
- **Model:** ViT-B/32, ViT-L/14
- **Embedding boyutu:** 512 (ViT-B), 768 (ViT-L)
- **Avantaj:** Açık kaynak, geniş topluluk, görüntü+metin aynı uzayda
- **Kullanım:** Görüntü ve metin sorguları aynı vektör uzayında

### SigLIP (Google)
- **Model:** siglip-so400m-patch14-384
- **Embedding boyutu:** 1152
- **Avantaj:** Daha iyi zero-shot performansı, daha hızlı

### Jina CLIP v2
- **Model:** jina-clip-v2
- **Embedding boyutu:** 1024
- **Avantaj:** 89 dil desteği, Türkçe dahil, Matryoshka representation

### Yefai için Karar
- **Varsayılan:** OpenCLIP ViT-B/32 (hafif, hızlı, iyi destek)
- **Yedek:** Jina CLIP v2 (Türkçe metin sorguları için daha iyi olabilir)
- **pgvector uyumluluğu:** Hepsi uyumlu (float32 vektör)

---

## 3. Zero-Shot Anomali Tespiti

### TimesFM 2.5 (Google)
- Zero-shot zaman serisi tahmini
- Milyarlarca veri noktasıyla önceden eğitilmiş, ağırlıklar dondurulmuş
- Context window ile çalışır: son N adım → next-step tahmini
- Eğitim döngüsü YOK — direkt inference
- HuggingFace'te mevcut: `google/timesfm-2.5-200m-pytorch`

### Anomalib (Intel)
- Endüstriyel anomali tespiti için açık kaynak kütüphane
- PatchCore algoritması: memory bank tabanlı, birkaç "sağlam" örnekle çalışır
- Hafif eğitim (few-shot) gerekebilir — TimesFM kadar zero-shot değil
- Alternatif: EfficientAD, FastFlow

### Füzyon Stratejisi
- Sensör anomali skoru (0-1) + Görüntü anomali skoru (0-1) → ağırlıklı ortalama
- Eşik: 0.7 (konfigüre edilebilir)
- Sensör ve görüntü aynı anda anomali → kesin anomali
- Sadece biri anomali → uyarı seviyesi düşük

---

## 4. pgvector vs Alternatif Vektör Veritabanları

| | pgvector | Pinecone | Qdrant | Weaviate |
|---|---------|----------|--------|----------|
| **Kurulum** | PostgreSQL eklentisi | Cloud SaaS | Docker / Cloud | Docker / Cloud |
| **Maliyet** | Ücretsiz | $70+/ay | Ücretsiz (self-host) | Ücretsiz (self-host) |
| **Gecikme** | <10ms (10K) | <5ms | <5ms | <10ms |
| **Filtreleme** | SQL WHERE | Metadata filter | Payload filter | GraphQL filter |
| **Yefai için** | ✅ Seçildi | ❌ | ❌ | ❌ |

### pgvector Avantajları
- PostgreSQL ile aynı yerde — ek servis yok
- SQL ile hibrit sorgu: vektör + metadata tek query'de
- Yerel (offline) çalışır, internet gerektirmez
- pgvector 0.7+ ile HNSW indexing, paralel index build

### pgvector Kurulum
```sql
CREATE EXTENSION vector;
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    image_id INTEGER REFERENCES images(id),
    embedding vector(512),  -- CLIP ViT-B/32
    text_embedding vector(512),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);
```

---

## 5. Tauri vs Electron

| | Tauri v2 | Electron |
|---|---------|----------|
| **Bundle boyutu** | ~10-20MB | ~120MB+ |
| **Bellek (boşta)** | ~50MB | ~200MB |
| **Motor** | OS WebView | Chromium |
| **Backend** | Rust | Node.js |
| **Güvenlik** | Yüksek (Rust) | Orta |
| **Ekosistem** | Büyüyor | Devasa |
| **Yefai için** | ✅ Seçildi | ❌ |

### Tauri + Next.js Mimarisi
- Next.js `output: "export"` ile static site olarak build edilir
- Tauri `tauri.conf.json` içinde `frontendDist: "../client/out"` gösterilir
- FastAPI, Tauri sidecar olarak başlatılır
- Rust komutları ile native özellikler (dosya sistemi, bildirim) frontend'e expose edilir

---

## 6. PUQ AI

**URL:** https://docs.puq.ai/
**Tip:** AI-first görsel workflow otomasyon platformu (Zapier/Make benzeri ama AI odaklı)

### Bulgular
- 200+ entegrasyon (Google, Microsoft, CRM'ler, Slack, veritabanları)
- Native AI node'ları: OpenAI, Claude, Mistral, ElevenLabs, Pinecone, Qdrant
- AI Router: Tek API üzerinden çoklu AI sağlayıcı
- Webhook ve schedule ile tetikleme

### Yefai için Değerlendirme
- **v1.0'da core entegrasyon** — FastAPI → PUQ AI webhook → Telegram/E-posta/SMS bildirimleri
- **Webhook client:** Anomali tespit anında PUQ AI workflow'unu tetikler
- **PUQ AI workflow'ları:** Telegram alert, E-posta raporu (görüntü ekli), SMS kritik uyarı, günlük/haftalık özet rapor
- **Fallback:** PUQ AI offline ise OS native notification + log'a yaz, retry mekanizması
- PUQ AI dokümanları ayrı bir inceleme olarak `server/docs/puqai-inceleme.md` dosyasında

---

## 7. MATWI Veri Seti Özellikleri

| Özellik | Değer |
|---------|-------|
| Toplam görüntü | 1663 |
| Set sayısı | 17 |
| Sensör kanalı | 5 (Accelerometer, Acoustic, Force X, Y, Z) |
| Takım çapı | 15mm (tüm setler) |
| Aşınma tipi | Flank wear, Adhesive wear, Combination |
| Aşınma ölçümü | Mikrometre (µm) |
| Sync sorunu | Var — bazı görüntülerde sensör yok, bazı sensörlerde görüntü yok |

---

*Last updated: 2026-05-15*
