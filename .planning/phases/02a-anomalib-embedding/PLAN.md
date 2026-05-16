---
phase: 2A
name: "Anomalib Training & Embedding Pipeline"
goal: "Anomalib PatchCore ile görüntü anomali modeli eğit, Torch model export et, Jina CLIP v2 ile batch embedding üret, pgvector'e yaz."
depends_on: "Phase 1"
estimated_effort: "2 hafta"
manual_gate: ""
parallel: true
parallel_with: "Phase 2B"
assignee: "Kişi A"
---

# Plan: Phase 2A — Anomalib Training & Embedding Pipeline

## Goal
Anomalib Python API ile PatchCore eğitimi yap, modeli .pt olarak export et. Jina CLIP v2 ile 1663 görüntü için embedding üret, pgvector'e yaz. Test setinde lokal inference çalıştır. FastAPI endpoint'lerini yaz.

## Prerequisites
- [x] Phase 1 tamamlandı (veri Supabase'de)
- [ ] Jina CLIP v2 modeli indirilebilir durumda (internet)
- [ ] `requirements.txt` güncel (anomalib, torch, transformers, supabase)

---

## Tasks

### Wave 1: Anomalib Setup & Data Prep

#### Task 1.1: Anomalib kurulumu ve veri hazırlığı
- **Files:** `server/ai/anomalib/setup.py`, `server/ai/anomalib/dataset.py`
- **Description:** 
  - `pip install anomalib` (veya GitHub'dan)
  - MATWI verisini Anomalib formatına dönüştür: normal (düşük wear) → train, anomalili → test
  - Anomalib `Folder` dataset formatı: `train/good/`, `test/good/`, `test/bad/`
  - Wear threshold belirle: wear > 75µm → anomaly
  - Train set: sadece normal/düşük aşınmalı görüntüler (few-shot, ~50-100 örnek)
- **UAT:** Anomalib dataset loader hatasız çalışır, train/test klasör yapısı doğru

#### Task 1.2: Image data quality report (anomalib öncesi)
- **Files:** `reports/image_data_quality.md`
- **Description:** Eksik görseller, wear/type dağılımı, anomaly threshold analizi. Hangi görüntüler train/hangileri test? Split manifest ile çapraz kontrol.
- **UAT:** Tüm görüntülerin wear değeri var, anomaly threshold istatistiksel olarak anlamlı

### Wave 2: Anomalib Training

#### Task 2.1: PatchCore eğitimi
- **Files:** `server/ai/anomalib/train.py`
- **Description:**
  ```python
  from anomalib.models import Patchcore
  from anomalib.engine import Engine
  
  model = Patchcore(
      backbone="wide_resnet50_2",
      layers=("layer2", "layer3"),
      pre_trained=True,
      coreset_sampling_ratio=0.1,
      num_neighbors=9
  )
  engine = Engine(max_epochs=1, devices=1)
  engine.fit(model, datamodule=train_dataloader)
  ```
  - Memory bank oluşturma (normal örneklerden patch feature'lar)
  - Coreset subsampling (k-center-greedy)
  - Model checkpoint kaydet
- **UAT:** Eğitim tamamlandı, memory bank boyutu > 0, loss log'landı

#### Task 2.2: Model export (.pt)
- **Files:** `server/ai/anomalib/export.py`
- **Description:** Eğitilen PatchCore modelini TorchScript veya torch.save ile `.pt` dosyasına export et. Model metadata'sını (backbone, layers, threshold) ayrı JSON'a yaz.
- **UAT:** `.pt` dosyası oluştu, `torch.load()` ile yüklenebiliyor, Phase 2B'nin kullanımına hazır

#### Task 2.3: Test setinde lokal inference
- **Files:** `server/ai/anomalib/inference.py`
- **Description:** 
  - Test setindeki tüm görüntüler için anomali skoru hesapla
  - Her görüntü için: anomaly_score (float 0-1), anomaly_map (heatmap)
  - Skor > threshold → anomaly etiketi
  - Sonuçları Supabase `anomalies` tablosuna yaz
- **UAT:** Test setindeki yüksek aşınmalı görüntüler anomaly olarak işaretlendi

#### Task 2.4: Aşınma tipi sınıflandırması
- **Files:** `server/ai/anomalib/wear_classifier.py`
- **Description:** 
  - labels.csv'deki `type` kolonunu kullan: Flank wear, Adhesive wear, Combination
  - Anomali tespit edilen görüntüler için tip sınıflandırması yap
  - Basit CNN classifier veya CLIP zero-shot yaklaşımı
  - Sonuçları `anomalies.wear_type` sütununa yaz
- **UAT:** En az %80 doğruluk, 3 sınıf da temsil ediliyor

### Wave 3: Jina CLIP v2 Embedding

#### Task 3.1: Jina CLIP v2 model setup
- **Files:** `server/ai/embeddings/model.py`
- **Description:**
  ```python
  from transformers import AutoModel
  model = AutoModel.from_pretrained(
      "jinaai/jina-clip-v2",
      trust_remote_code=True,
      torch_dtype=torch.float16
  )
  ```
  - Model download + cache (`~/.cache/huggingface/`)
  - GPU varsa CUDA, yoksa MPS (M2 Pro) veya CPU
  - Model warmup: ilk inference gecikmesini ölç
- **UAT:** Model yüklendi, encode_image() ve encode_text() çalışıyor

#### Task 3.2: Batch embedding pipeline
- **Files:** `server/ai/embeddings/batch_embed.py`
- **Description:**
  - 1663 görüntü için batch embedding (batch_size=32)
  - MRL opsiyonu: 1024-dim → 64/128/256 (config'den seçilir)
  - Progress bar, hata toleransı (bozuk görüntüyü atla, log'a yaz)
  - Her embedding'i `(image_id, vector)` olarak Supabase'e yaz
- **UAT:** 1663 embedding < 30 saniyede üretildi, pgvector'de sorgulanabiliyor

#### Task 3.3: Embedding arama endpoint'i
- **Files:** `server/ai/embeddings/search.py`
- **Description:**
  - Cosine similarity search: `image_embedding <=> query_vector`
  - Top-K sonuç, metadata ile birlikte
  - Hibrit arama: vektör similarity + SQL WHERE (set, wear, date)
- **UAT:** "Set 5'teki flank wear görüntüleri" sorgusu doğru sonuç dönüyor

### Wave 4: FastAPI Endpoint'leri

#### Task 4.1: Anomalib router
- **Files:** `server/routers/anomalib.py`, `server/services/anomalib_service.py`
- **Description:**
  - `POST /api/anomalib/train` — eğitim başlat (background task)
  - `GET /api/anomalib/status/{job_id}` — eğitim durumu sorgula
  - `POST /api/anomalib/predict` — tek görüntü için inference
  - `GET /api/anomalib/model/info` — yüklü model bilgisi
- **UAT:** Swagger UI'da tüm endpoint'ler görünür ve çalışır

#### Task 4.2: Embedding router
- **Files:** `server/routers/embeddings.py`, `server/services/embedding_service.py`
- **Description:**
  - `POST /api/embeddings/generate` — batch embedding tetikle
  - `POST /api/embeddings/search` — vektör arama (body: query_text veya query_image_base64, top_k)
  - `GET /api/embeddings/image/{image_id}` — tek görüntü embedding'i
- **UAT:** Metin sorgusu ile ilgili görüntüler dönüyor

---

## Verification

- [ ] PatchCore eğitimi tamamlandı, memory bank oluştu
- [ ] Model .pt dosyası export edildi, Phase 2B için hazır
- [ ] Test setinde anomali skorları hesaplandı, Supabase'e yazıldı
- [ ] Aşınma tipi sınıflandırması çalışıyor
- [ ] 1663 embedding pgvector'de, cosine similarity search çalışıyor
- [ ] Tüm FastAPI endpoint'leri Swagger'da dokümante

## must_haves

1. **Eğitilmiş PatchCore modeli (.pt)** — Phase 2B NovaVision inference için
2. **1663 embedding pgvector'de** — Phase 3A RAG için
3. **Cosine similarity search çalışıyor** — Phase 3A RAG'ın core fonksiyonu
4. **Anomaly skorları Supabase'de** — Phase 3B bildirim tetikleme için
5. **Model .pt erişilebilir** — Phase 4 entegrasyon için

## Deliverables
- `server/ai/anomalib/train.py` + `export.py` + `inference.py`
- `server/ai/anomalib/wear_classifier.py`
- `server/ai/embeddings/model.py` + `batch_embed.py` + `search.py`
- Eğitilmiş model: `models/patchcore_matwi.pt`
- `reports/image_data_quality.md`
- `server/routers/anomalib.py` + `server/routers/embeddings.py`
- `server/services/anomalib_service.py` + `server/services/embedding_service.py`
