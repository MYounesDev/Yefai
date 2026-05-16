---
phase: 1
name: "Veri Altyapısı & Supabase Setup"
goal: "MATWI veri setini işle, Supabase şemasını kur, mock yedek parça verisini üret, FastAPI proje iskeletini oluştur."
depends_on: ""
estimated_effort: "1.5 hafta"
manual_gate: "G1 — Supabase projesi oluşturulmuş, pgvector aktif, connection string .env'de olmalı"
parallel: false
assignee: "birlikte"
---

# Plan: Phase 1 — Veri Altyapısı & Supabase Setup (Hibrit)

## Goal
17 MATWI zip dosyasını local'e ayıkla, train/test split yap. Supabase'e SADECE metadata + embedding vektörleri için hafif şema kur. Görüntü ve sensör dosyaları local diskte kalır (~400MB). Mock yedek parça verisini üret. FastAPI proje iskeletini kur.

**Mimari:** Görüntüler local diskten serve edilir. Supabase sadece metadata + pgvector embedding (~10MB).

## Prerequisites (Manual Gate)
- [x] **G1:** Supabase projesi oluşturuldu (supabase.com) — Yefai `jgufisddsdmappcnglcf`
- [x] pgvector extension enable edildi — `vector` 0.8.0 doğrulandı
- [x] `SUPABASE_URL` ve `SUPABASE_SERVICE_KEY` `.env` dosyasına yazıldı — Yefai project env hazır
- [x] Supabase dashboard/API bağlantısı test edildi — REST auth HTTP 200

---

## Tasks

### Wave 1: Veri Ayıklama & Parse

#### Task 1.1: Zip ayıklama pipeline'ı
- **Files:** `server/etl/unzip_data.py`
- **Description:** 17 zip dosyasını `server/dataset/` altından oku, `data/MATWI/Set*/` yapısına ayıkla. labels.csv ve sets.csv'yi oku. Her set için görüntü sayısını doğrula.
- **UAT:** Ayıklanan dosya sayısı = labels.csv'deki satır sayısı (1663 görüntü)

#### Task 1.2: labels.csv ve sets.csv parser
- **Files:** `server/etl/parse_labels.py`
- **Description:** labels.csv'den ImageFile, wear, type, Set, ImageDateTime kolonlarını parse et. sets.csv'den set metadata'sını çıkar. DataFrame olarak normalize et.
- **UAT:** Tüm kolonlar eksiksiz parse edildi, wear değerleri float, timestamp'ler datetime

#### Task 1.3: Sensör CSV parser
- **Files:** `server/etl/parse_sensors.py`
- **Description:** Her set için Accelerometer, Acoustic, Force X/Y/Z CSV'lerini parse et. Timestamp bazlı sırala. Eksik/bozuk CSV'leri logla.
- **UAT:** Her sensör dosyası 6 kolon olarak okundu (timestamp + 5 kanal)

### Wave 2: Split & Supabase Schema

#### Task 2.1: Train/test split (set-bazlı)
- **Files:** `server/etl/split_data.py`
- **Description:** %70/%30 split — set ID bazında, aynı set asla bölünmez. 17 set → 12 train, 5 test. Split manifest'ini `data/manifests/split_manifest.csv` olarak kaydet.
- **UAT:** Test setindeki hiçbir Set ID train'de yok. Split oranı %70 ± %3.

#### Task 2.2: Supabase migration script (hafif)
- **Files:** `server/db/migrations/001_initial_schema.sql`
- **Description:** SQL migration — **sadece metadata + vektör:**
  ```sql
  CREATE TABLE sets (id SERIAL PRIMARY KEY, name TEXT, image_count INT);
  CREATE TABLE images (
    id SERIAL PRIMARY KEY, set_id INT REFERENCES sets(id),
    file_path TEXT,  -- local path, örn: data/MATWI/Set3/images/img_001.png
    flank_wear FLOAT, adhesive_wear FLOAT, combination_wear FLOAT,
    wear_type TEXT, timestamp TIMESTAMP,
    image_embedding vector(1024)  -- Jina CLIP v2
  );
  CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY, image_id INT REFERENCES images(id),
    score FLOAT, wear_type TEXT, detected_at TIMESTAMP
  );
  CREATE INDEX ON images USING hnsw (image_embedding vector_cosine_ops);
  ```
  - **Görüntü BLOB'u yok** — `file_path` local disk yolunu tutar
  - **Sensör CSV'leri local'de** — `sensors` tablosu Supabase'de yok
- **UAT:** Migration Supabase'de hatasız çalışır, ~10MB veri

#### Task 2.3: Supabase Python client setup
- **Files:** `server/db/client.py`, `server/db/config.py`
- **Description:** `supabase-py` ile bağlantı. `.env`'den SUPABASE_URL ve SUPABASE_SERVICE_KEY oku. Connection pool yapılandır. Test query çalıştır.
- **UAT:** `client.table("sets").select("*").execute()` başarılı

### Wave 3: Veri Yükleme & Mock Veri

#### Task 3.1: Supabase'e metadata yükleme
- **Files:** `server/etl/seed_database.py`
- **Description:** SADECE metadata'yı Supabase'e yükle: sets → images (file_path + wear + type + timestamp, **görüntü BLOB'u yok**). Görüntü ve sensör dosyaları local diskte `data/MATWI/` altında kalır. Batch insert (100'er row). Progress bar.
- **UAT:** `SELECT COUNT(*) FROM images` = 1663, tüm file_path'ler geçerli local path

#### Task 3.2: Mock yedek parça verisi üretimi
- **Files:** `server/etl/generate_mock_spare_parts.py`
- **Description:** `.planning/yedek-parca-krizi-mock-plan.md` referansına göre:
  - `spare_parts_catalog`: 30-50 parça, kritiklik seviyeleri (A/B/C)
  - `suppliers`: 8-12 tedarikçi, lead time, güvenilirlik skoru
  - `inventory_snapshots`: her parça için stok, siparişte, min/max seviye
  - `part_tickets`: açık ticket'lar (waiting_part, ordered, stockout)
  - `purchase_orders`: geçmiş ve aktif PO'lar
  - CSV olarak üret, Supabase'e yükle
- **UAT:** Tüm mock tablolar dolu, kriz senaryosu için en az 3 "crisis" durumu var

### Wave 4: Kalite Raporu & FastAPI İskeleti

#### Task 4.1: Veri kalite raporu
- **Files:** `reports/data_quality_report.md`
- **Description:** Görüntü-sensör timestamp eşleştirme, eşleşen çift sayısı, eksik/bozuk veri. Wear dağılımı, type dağılımı. Split özeti.
- **UAT:** Eşleşen çift > %90, tüm eksikler log'landı

#### Task 4.2: Mock yedek parça kalite raporu
- **Files:** `reports/mock_spare_parts_report.md`
- **Description:** Kritiklik dağılımı (A/B/C), stok açığı olan parçalar, ticket durum dağılımı, kriz skoru dağılımı. Dağılımın gerçekçiliği kontrolü.
- **UAT:** En az 1 "crisis" (skor > 70), en az 3 "at_risk" (skor 40-70) örneği

#### Task 4.3: FastAPI proje iskeleti
- **Files:** `server/main.py`, `server/config.py`, `server/deps.py`
- **Description:** 
  - FastAPI app oluştur (lifespan placeholder)
  - Router yapısı: `server/routers/` (anomalib.py, novavision.py, embeddings.py, chat.py, notifications.py, spare_parts.py)
  - Config: `.env` loader (pydantic-settings)
  - Deps: Supabase client dependency injection
  - CORS middleware (frontend için hazır)
- **UAT:** `uvicorn server.main:app` çalışır, `GET /health` 200 döner

---

## Verification

- [ ] Tüm zip'ler ayıklandı, 1663 görüntü erişilebilir
- [ ] Train/test split set-bazlı, leakage yok
- [ ] Supabase'de tüm tablolar var, pgvector aktif
- [ ] Mock yedek parça verisi kriz senaryolarını kapsıyor
- [ ] Veri kalite raporu eksikleri belgeliyor
- [ ] FastAPI scaffold çalışır durumda

## must_haves

1. **1663 görüntü + sensör verisi Supabase'de** — Phase 2A ve 2B'nin çalışması için
2. **Train/test split set-bazlı, leakage yok** — Model eğitiminin güvenilirliği için
3. **pgvector vector(1024) sütunu + HNSW index** — Phase 2A embedding'leri için
4. **Mock yedek parça tabloları dolu** — Phase 3B kriz otomasyonu için
5. **FastAPI scaffold çalışıyor** — Tüm sonraki fazların temeli

## Deliverables
- Dolu Supabase veritabanı (8+ tablo)
- `reports/data_quality_report.md`
- `reports/mock_spare_parts_report.md`
- `data/manifests/split_manifest.csv`
- Çalışan FastAPI scaffold (`server/main.py` + router iskeleti)
