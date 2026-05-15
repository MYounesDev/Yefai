# Research Synthesis — Yefai Project

> Domain araştırması, teknoloji seçimleri, rakip/platform incelemeleri.
> Her bulgu PROJECT.md veya ROADMAP.md'deki bir kararı besler.

---

## 1. Supabase (Veritabanı)

**URL:** https://supabase.com/
**Tip:** Managed PostgreSQL + built-in pgvector, auth, real-time, dashboard

### Bulgular
- PostgreSQL 16 tabanlı, pgvector built-in (ek eklenti kurulumu gerektirmez)
- Row-level security (RLS), built-in auth
- Web dashboard ile tablo yönetimi ve sorgu
- 500MB ücretsiz tier (demo için yeterli)
- Python SDK (`supabase-py`), SQL client uyumluluğu

### Yefai için Değerlendirme
- **v1.0'da core veritabanı** — local PostgreSQL yerine managed Supabase
- pgvector ekstra kurulum gerektirmediği için Phase 1 hızlanır
- Dashboard üzerinden hızlı schema iteration ve veri keşfi
- İleride auth özelliği eklenirse built-in auth kullanılabilir

### Supabase Schema (Planlanan)
```sql
CREATE TABLE sets (id SERIAL PRIMARY KEY, name TEXT, image_count INT);
CREATE TABLE images (id SERIAL PRIMARY KEY, set_id INT REFERENCES sets(id),
  file_path TEXT, flank_wear FLOAT, adhesive_wear FLOAT, combination_wear FLOAT,
  image_embedding vector(1024)  -- Jina CLIP v2
CREATE TABLE sensors (id SERIAL PRIMARY KEY, image_id INT REFERENCES images(id),
  timestamp TIMESTAMP, accelerometer FLOAT[], acoustic FLOAT[], force_x FLOAT[],
  force_y FLOAT[], force_z FLOAT[]);
CREATE TABLE anomalies (id SERIAL PRIMARY KEY, image_id INT REFERENCES images(id),
  score FLOAT, wear_type TEXT, detected_at TIMESTAMP);
CREATE INDEX ON images USING hnsw (image_embedding vector_cosine_ops);
```

---

## 2. TimesFM 2.5 — ERTELENDİ (v1.1+)

**Model:** Google TimesFM 2.5 — Zero-shot zaman serisi foundation modeli
**Paper:** arxiv:2310.10688
**HF:** `google/timesfm-2.5-200m-pytorch`

### Neden Ertelendi?
- v1.0'da SADECE görüntü tabanlı anomali tespiti yapılacak
- TimesFM sensör verisiyle prediction-based anomaly detection için
- v1.0 kapsamını daraltmak ve hızlı demo çıkarmak için sonraya bırakıldı

### v1.1+ Planı
- Zero-shot inference ile başla (eğitimsiz, direkt kullan)
- Son 50 sensör adımı → next-step tahmini → gerçek vs tahmin = anomali skoru
- Vakit ve veri olursa fine-tune (MATWI sensör verisiyle)

### Nasıl Çalışır (Referans)
```python
import timesfm
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")
model.compile(timesfm.ForecastConfig(max_context=1024, max_horizon=256, ...))
point, quantiles = model.forecast(horizon=1, inputs=[sensor_history])
# forecast vs actual → anomaly score
```

---

## 3. NovaVision AI

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
- **Doğrudan embedding için kullanılamaz** — Jina CLIP v2 gibi açık modeller kullanılacak
- **Potansiyel entegrasyon:** İleride görüntü işleme pipeline'ı olarak (v1.1+)
- **Alternatif embedding:** Jina CLIP v2 (seçildi), SigLIP, OpenCLIP
- NovaVision'ın "Predictive Maintenance" ve "Equipment Inspection" uygulamaları konsept olarak Yefai'ye benziyor — rakip değil, potansiyel iş birliği

---

## 4. Embedding Modeli: Jina CLIP v2 (TEK MODEL)

**Model:** `jinaai/jina-clip-v2`
**Parametre:** 865M
**Vektör boyutu:** 1024 (MRL ile 64'e kadar kısaltılabilir)
**Dil:** 89 dil (Türkçe dahil — HF tags: `tr`)
**Lisans:** CC-BY-NC-4.0 (demo için uygun, ticari için değişebilir)

### Neden Tek Model?
- v1.0'da eskiden 2 model vardı: EmbeddingGemma 300M (metin) + Gemini Embedding 2 (multimodal, API)
- Jina CLIP v2 **hem görüntü hem metin** embedding'ini aynı vektör uzayında yapar
- Tek model = daha az bağımlılık, daha basit pipeline, API maliyeti yok
- RAG chatbot için ideal: kullanıcı sorusu (metin) ve görüntüler aynı uzayda

### Avantajları
- **Türkçe desteği** kanıtlanmış (89 dil, HF tags'de `tr`)
- **Matryoshka (MRL):** 1024 boyutlu vektörü 64'e kadar kısalt, pgvector'de 16x depolama tasarrufu
- **Cross-modal benchmark:** 0.873 (CLIP'ten %14 daha iyi, Milvus CCKM Mart 2026)
- **Lokal inference:** API yok, internet yok, ücretsiz
- **M2 Pro'da çalışır:** 865M parametre, ~2GB RAM, 1663 görüntü < 20sn

### Kullanım
```python
from transformers import AutoModel
model = AutoModel.from_pretrained("jinaai/jina-clip-v2", trust_remote_code=True)

# Görüntü embedding
image_emb = model.encode_image(image)  # (1024,)

# Türkçe metin embedding
text_emb = model.encode_text("flank wear aşınması olan takım")  # (1024,)

# Cosine similarity
from torch.nn.functional import cosine_similarity
score = cosine_similarity(image_emb, text_emb, dim=-1)
```

### Neden CLIP/SigLIP/EmbeddingGemma Değil?
| Model | Görüntü | Metin | Türkçe | Parametre | Sonuç |
|-------|---------|-------|--------|-----------|-------|
| Jina CLIP v2 | ✅ | ✅ | ✅ 89 dil | 865M | **Seçildi** |
| OpenCLIP ViT-B/32 | ✅ | ✅ | Orta | 150M | Hafif alternatif |
| SigLIP SO400M | ✅ | ✅ | Orta | 400M | Daha iyi görüntü, Türkçe zayıf |
| EmbeddingGemma 300M | ❌ | ✅ | ✅ | 300M | Görüntü yapamaz |
| Gemini Embedding 2 | ✅ | ✅ | ✅ | 9B | API, paralı, overkill |

### v1.1+ için Not
CC-BY-NC lisans ticari kullanımda sorun çıkarırsa Apache 2.0 alternatifler: SigLIP (Google) veya Qwen3-VL-2B (Alibaba). Jina CLIP v2 API'si de değerlendirilebilir.

---

## 5. Görüntü Anomali Tespiti (Anomalib)

### Anomalib PatchCore (Intel)
- Endüstriyel anomali tespiti için açık kaynak kütüphane
- PatchCore algoritması: memory bank tabanlı, birkaç "sağlam" örnekle eğitilir
- Few-shot: train setindeki normal görüntülerle memory bank oluşturulur
- Test setinde anomali skoru hesaplanır, eşik üstü → anomali
- Aşınma tipi sınıflandırması: Flank wear, Adhesive wear, Combination
- Alternatif: EfficientAD, FastFlow

### Neden Sadece Görüntü?
- MATWI'de asıl sinyal görüntüde (aşınma gözle görünür, µm etiketli)
- Sensör verisi yardımcı kanal, dashboard'da canlı grafik olarak gösterilir
- v1.0 kapsamını daraltmak için sensör anomali tespiti (TimesFM) ertelendi
- v1.1+'da sensör füzyonu eklenecek

### Train/Test Akışı
```
MATWI (17 set) → %70 train, %30 test
Train → Anomalib PatchCore.fit(normal_images) → memory bank
Test → PatchCore.predict(image) → anomaly_score (0-1)
score > threshold → ANOMALİ (aşınma tipi ile birlikte)
```

---

## 6. pgvector (Supabase Built-in)

| | pgvector | Pinecone | Qdrant | Weaviate |
|---|---------|----------|--------|----------|
| **Kurulum** | PostgreSQL eklentisi | Cloud SaaS | Docker / Cloud | Docker / Cloud |
| **Maliyet** | Ücretsiz | $70+/ay | Ücretsiz (self-host) | Ücretsiz (self-host) |
| **Gecikme** | <10ms (10K) | <5ms | <5ms | <10ms |
| **Filtreleme** | SQL WHERE | Metadata filter | Payload filter | GraphQL filter |
| **Yefai için** | ✅ Seçildi | ❌ | ❌ | ❌ |

### pgvector Avantajları (Supabase'de)
- Supabase'de built-in — `CREATE EXTENSION vector` gerekmez, otomatik aktif
- SQL ile hibrit sorgu: vektör + metadata tek query'de
- Supabase dashboard üzerinden tablo yönetimi ve sorgu
- HNSW indexing built-in
- 500MB ücretsiz tier (demo için yeterli)

### Supabase pgvector Kullanımı
```sql
-- Supabase'de pgvector zaten aktif, direkt kullan
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    set_id INTEGER REFERENCES sets(id),
    file_path TEXT,
    image_embedding vector(1024)  -- Jina CLIP v2 (MRL ile 64'e kısaltılabilir)
);
CREATE INDEX ON images USING hnsw (image_embedding vector_cosine_ops);

-- Vektör arama
SELECT * FROM images
ORDER BY image_embedding <=> query_vector
LIMIT 5;
```

---

## 7. Tauri vs Electron

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

## 8. PUQ AI

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

## 9. MATWI Veri Seti Özellikleri

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
