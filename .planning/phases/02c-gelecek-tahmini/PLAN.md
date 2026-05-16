---
phase: 2.5
name: "Gelecek Tahmini (Wear Prediction Engine)"
goal: "Anomalib skorlarından aşınma seviyesi tahmini, lineer regresyon ile aşınma hızı, kritik eşiğe kalan süre, senaryo analizi, tahmin API endpoint'leri."
depends_on: "Phase 2A (anomali skorları Supabase'de), Phase 1"
estimated_effort: "1 hafta"
manual_gate: ""
parallel: true
parallel_with: "Phase 3A, Phase 3B başlangıcı"
assignee: "Kişi B (2B bitince)"
---

# Plan: Phase 2.5 — Gelecek Tahmini (Wear Prediction Engine)

## Goal
Anomalib'in ürettiği anomali skorlarını kullanarak aşınma hızı hesapla, kritik eşiğe kalan süreyi tahmin et, 3 senaryolu projeksiyon yap. Backend-only: veriyi üret, API'den sun. Grafik/frontend yok.

**Temel mantık:**
```
Anomalib score (0-1) → kalibre edilmiş aşınma µm
Son N kontrolün aşınma değerleri → lineer regresyon → aşınma hızı (µm/saat)
Mevcut aşınma + hız → kritik eşiğe kalan süre (saat)
3 senaryo: mevcut hız / hızlanırsa (+%25) / yavaşlarsa (-%25)
```

## Prerequisites
- [x] Phase 2A'da anomaliler Supabase `anomalies` tablosuna yazılmış olmalı
- [x] En az 3-4 kontrol noktası olan takımlar var (aynı set içinde)
- [ ] NumPy/SciPy kurulu (`pip install numpy scipy`)

---

## Tasks

### Wave 1: Aşınma Hızı Hesaplama Engine

#### Task 1.1: Skor → µm kalibrasyon
- **Files:** `server/ai/prediction/calibration.py`
- **Description:**
  - Anomalib anomali skoru (0-1) ile gerçek aşınma seviyesi (µm) arasında mapping
  - Kalibrasyon stratejisi:
    - labels.csv'deki gerçek wear değerlerini kullan
    - skor 0.0 → 0 µm, skor 0.5 → 100 µm, skor 1.0 → 200+ µm
    - Lineer interpolasyon: `wear_um = score * 200`
    - Alternatif: skor-wear scatter plot'tan polynomial fit
  - Kalibrasyon doğruluğunu ölç: MAE, RMSE
  - Supabase'den tüm anomali skorlarını oku, her birine `estimated_wear_um` ekle
- **UAT:** labels.csv'deki gerçek wear ile tahmin edilen wear arasındaki MAE < 30µm

#### Task 1.2: Aşınma hızı hesaplama
- **Files:** `server/ai/prediction/wear_rate.py`
- **Description:**
  - Aynı takımın (aynı set içindeki) son N kontrolünü Supabase'den çek
  - Zaman damgalarına göre sırala
  - Lineer regresyon: `scipy.stats.linregress(timestamps, wear_values)`
  - Çıktı: `wear_rate_um_per_hour` (eğim), `r_squared` (uyum kalitesi)
  - Minimum 3 veri noktası gerekli, yoksa "yetersiz veri" hatası
  - Edge case: tek kontrol noktası → hız hesaplanamaz
- **UAT:** 5 kontrollü bir set için aşınma hızı hesaplanıyor, r² > 0.7

#### Task 1.3: Kritik eşik projeksiyonu
- **Files:** `server/ai/prediction/projection.py`
- **Description:**
  - `hours_to_critical = (CRITICAL_THRESHOLD_UM - current_wear_um) / wear_rate_um_per_hour`
  - Kritik eşik: 200 µm (config'den değiştirilebilir)
  - Negatif çıkarsa → zaten kritik durumda, 0 saat
  - Hız çok düşükse → 999 saat (pratikte sonsuz)
  - Güven göstergesi:
    - `high`: r² > 0.85 ve en az 5 veri noktası
    - `medium`: r² > 0.6 ve en az 3 veri noktası
    - `low`: r² < 0.6 veya az veri
- **UAT:** Kritik eşiğe 20 saat kalan bir takım için doğru hesaplanıyor

### Wave 2: Senaryo Analizi

#### Task 2.1: 3 senaryolu projeksiyon
- **Files:** `server/ai/prediction/scenarios.py`
- **Description:**
  - 3 senaryo, sabit çarpanlarla:
    1. **Baseline (mevcut hız):** wear_rate × 1.0 → lineer projeksiyon
    2. **Pessimistic (hızlanırsa):** wear_rate × 1.25 → daha erken kritik
    3. **Optimistic (yavaşlarsa):** wear_rate × 0.75 → daha geç kritik
  - Her senaryo için:
    - `hours_to_critical`
    - `estimated_critical_time` (ISO timestamp)
    - Projeksiyon dizisi: `[{timestamp, wear_um}, ...]` (grafik için hazır)
  - Çıktı formatı:
    ```json
    {
      "scenarios": {
        "baseline": {"hours": 20, "critical_at": "2026-05-17T06:00:00Z"},
        "pessimistic": {"hours": 16, "critical_at": "2026-05-17T02:00:00Z"},
        "optimistic": {"hours": 27, "critical_at": "2026-05-17T13:00:00Z"}
      },
      "projection_points": [...]
    }
    ```
- **UAT:** 3 senaryo da mantıklı aralıkta (optimistic > baseline > pessimistic saat)

#### Task 2.2: Aşınma trend analizi
- **Files:** `server/ai/prediction/trends.py`
- **Description:**
  - Son 3 kontrolde hız değişimi: artıyor mu, azalıyor mu, sabit mi?
  - Trend tespiti: `trend = "accelerating" | "stable" | "decelerating"`
  - Hız değişim yüzdesi: son 2 periyot arası fark
  - Uyarı eşiği: hız %15'ten fazla artmışsa "accelerating" → bildirimde vurgula
- **UAT:** Artan/azalan/sabit trend doğru tespit ediliyor

### Wave 3: DB Migration & API

#### Task 3.1: anomalies tablosuna yeni alanlar
- **Files:** `server/db/migrations/003_prediction_fields.sql`
- **Description:**
  ```sql
  ALTER TABLE anomalies ADD COLUMN estimated_wear_um FLOAT;
  ALTER TABLE anomalies ADD COLUMN wear_rate_um_per_hour FLOAT;
  ALTER TABLE anomalies ADD COLUMN hours_to_critical FLOAT;
  ALTER TABLE anomalies ADD COLUMN confidence TEXT CHECK (confidence IN ('low','medium','high'));
  ```
  - Migration Supabase'de çalıştır
  - Phase 1'deki seed script'ine bu alanları ekle (opsiyonel, sonradan doldurulacak)
- **UAT:** Kolonlar eklendi, constraint'ler çalışıyor

#### Task 3.2: Tahmin API endpoint'leri
- **Files:** `server/routers/predictions.py`, `server/services/prediction_service.py`
- **Description:**
  - `GET /api/predictions/{machine_id}` 
    - Response:
      ```json
      {
        "machine_id": "Set3",
        "current_wear_um": 145.0,
        "critical_threshold_um": 200.0,
        "wear_rate_um_per_hour": 2.8,
        "hours_to_critical": 19.6,
        "confidence": "medium",
        "trend": "stable",
        "scenarios": { ... },
        "projection_points": [ ... ],
        "last_check_at": "2026-05-16T10:00:00Z"
      }
      ```
  - `GET /api/predictions/factory/overview`
    - Tüm set'lerin özet durumu: current_wear, hours_to_critical, status (green/yellow/red)
    - Response: `{ "machines": [{ "machine_id": "Set3", "status": "warning", "hours": 20, ... }, ...] }`
  - `POST /api/predictions/recalculate/{machine_id}` — manuel yeniden hesaplama tetikle
- **UAT:** Swagger UI'da tüm endpoint'ler, örnek Set3 için anlamlı tahmin dönüyor

#### Task 3.3: Phase 3B entegrasyon noktası
- **Files:** `server/services/prediction_service.py` (dokümantasyon)
- **Description:**
  - Phase 3B'deki `crisis_service.py` bu endpoint'i tüketecek:
    ```python
    # crisis_service.py içinde:
    prediction = await prediction_service.get_prediction(machine_id)
    if prediction.hours_to_critical < spare_part.lead_time_hours:
        crisis_score += 30  # lead time yetişmiyor
    ```
  - Bu task sadece interface tanımı ve dokümantasyon — entegrasyon Phase 3B'de yapılacak
- **UAT:** `GET /api/predictions/{id}` response'u crisis_service'in beklediği formatta

---

## Verification

- [ ] Skor → µm kalibrasyonu çalışıyor, MAE < 30µm
- [ ] En az 3 kontrollü bir set için aşınma hızı hesaplanıyor
- [ ] Kritik eşik projeksiyonu mantıklı (pozitif, 200µm'ye yaklaşıyor)
- [ ] 3 senaryo (baseline/pessimistic/optimistic) doğru sıralamada
- [ ] Trend analizi: accelerating/stable/decelerating
- [ ] `/api/predictions/{machine_id}` anlamlı veri dönüyor
- [ ] `/api/predictions/factory/overview` tüm set'leri listeliyor
- [ ] Migration çalıştı, yeni kolonlar var

## must_haves

1. **Aşınma hızı hesaplanabiliyor** — En az 3 veri noktası olan takımlar için
2. **Kritik eşiğe kalan süre** — `hours_to_critical` doğru hesaplanıyor
3. **3 senaryolu projeksiyon** — Frontend'in grafik çizmesi için hazır veri
4. **`/api/predictions/factory/overview`** — Tüm makinelerin durum özeti
5. **Phase 3B'ye hazır interface** — crisis_service prediction'ları tüketebilir

## Deliverables
- `server/ai/prediction/calibration.py` + `wear_rate.py` + `projection.py`
- `server/ai/prediction/scenarios.py` + `trends.py`
- `server/routers/predictions.py`
- `server/services/prediction_service.py`
- `server/db/migrations/003_prediction_fields.sql`
