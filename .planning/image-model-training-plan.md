# Image Model Eğitim ve Çalıştırma Planı — Yefai v1.0

> Amaç: MATWI görüntülerinden görüntü tabanlı aşınma/anomali modeli eğitmek, çalıştırmak ve çıktılarını dashboard/RAG/bildirim fazlarına hazır hale getirmek.
> v1.0 kısıtı: Sensör verisi model eğitiminde kullanılmaz; sensör verisi sadece eşleştirme, canlı grafik ve ilerideki v1.1+ çalışmalar için tutulur.

---

## 1. İncelenecek Ana CSV ve Veri Dosyaları

### Zorunlu CSV

#### `data/labels.csv`

Image model eğitimi için ana label dosyası budur.

Mevcut kolonlar:

```text
ImageName, SensorName, Set, ImageID, SensorID, wear, type,
ImageDateTime, SensorDateTime, ImageFile, SensorFile
```

Image-only eğitimde kritik kolonlar:

| Kolon | Kullanım |
|-------|----------|
| `ImageFile` | Görüntünün path'i. Modelin okuyacağı dosya. |
| `wear` | Aşınma miktarı. Binary anomali label'ı ve tahmin paneli için kullanılır. |
| `type` | Aşınma tipi: `flank_wear`, `adhesion`, `flank_wear+adhesion`, boş. |
| `Set` | Leakage olmayan train/test split için kullanılır. Aynı set hem train hem test'e girmemeli. |
| `ImageDateTime` | Zaman sıralaması, trend/tahmin ve debug için kullanılır. |
| `ImageName` | Dosya adı kontrolü/debug için kullanılır. |

Mevcut hızlı özet:

```text
Satır sayısı: 1803
Set sayısı: 17
Set'ler: 1..17
wear min/max/ortalama: 15.0 / 750.0 / ~109.53

type dağılımı:
- flank_wear: 1154
- flank_wear+adhesion: 335
- adhesion: 179
- boş: 135
```

### Görüntü dosyaları

Planlanan canonical image root:

```text
data/MATWI/Set*/images/*.jpg
```

Şu an repoda gözlenen kısmi çıkarılmış veri:

```text
llm_docs/Set13/images/*.jpg
llm_docs/Set13/sensordata/*.csv
llm_docs/Set13.zip
```

Not: `labels.csv` içindeki `ImageFile` değerleri `MATWI/Set13/images/...` gibi başlıyor. Mevcut `llm_docs/Set13` çıkarımında ise path `llm_docs/Set13/images/...` şeklinde. Manifest üretirken path resolver şu adayları kontrol etmeli:

1. `<project_root>/<ImageFile>`
2. `<project_root>/data/<ImageFile>`
3. `<project_root>/llm_docs/<ImageFile>`
4. `<project_root>/llm_docs/<ImageFile without "MATWI/">`

Örnek:

```text
CSV ImageFile:
MATWI/Set13/images/Test_0015_1_02_012_2023-03-16T09_26_06.353427.jpg

Mevcut bulunan dosya:
llm_docs/Set13/images/Test_0015_1_02_012_2023-03-16T09_26_06.353427.jpg
```

### Sensör CSV'leri

Image model eğitimi için zorunlu değildir.

İlgili kolonlar:

```text
SensorName, SensorID, SensorDateTime, SensorFile
```

Kullanım alanı:

- Phase 1 veri kalite raporu
- görüntü-sensör timestamp eşleştirme
- Phase 4 dashboard canlı sensör grafikleri
- v1.1+ TimesFM / sensor anomaly detection

v1.0 image model eğitiminde input olarak kullanılmaz.

---

## 2. Label Stratejisi

### 2.1 Binary anomaly label

`wear` kolonundan türetilecek.

Başlangıç önerisi:

```text
wear <= 45   => normal / low_wear      => anomaly_label = 0
wear >= 90   => anomaly / high_wear     => anomaly_label = 1
45 < wear < 90 => mild / transition     => eğitimden çıkar veya sadece validation/test'te tut
```

Neden:

- Dataset'te tamamen sıfır aşınma görünmüyor; minimum wear 15.0.
- PatchCore için train tarafında mümkün olduğunca düşük aşınmalı/normal örnekler gerekir.
- Orta aşınma örnekleri modelin normal/anomali sınırını kirletebilir.

Alternatif threshold denemeleri:

```text
normal: wear <= 30, anomaly: wear >= 90
normal: wear <= 45, anomaly: wear >= 100
normal: wear <= 60, anomaly: wear >= 120
```

Her threshold için validation sonucu ayrı raporlanmalı.

### 2.2 Wear type classification label

`type` kolonundan alınır.

Normalize edilecek sınıflar:

```text
flank_wear           => flank_wear
adhesion             => adhesion
flank_wear+adhesion  => combination
boş                  => unknown veya eğitimden çıkar
```

v1.0 önerisi:

- İlk sınıflandırma eğitiminde boş `type` satırlarını çıkar.
- `flank_wear+adhesion` değerini `combination` olarak normalize et.
- Sınıf dengesizliği raporlanmadan accuracy tek başına başarı metriği sayılmamalı.

### 2.3 Regression label

`wear` doğrudan regresyon hedefi olarak kullanılabilir.

Ama v1.0 önceliği:

1. Binary anomaly detection
2. Wear type classification
3. Wear regression / estimated_wear_um

Regresyon daha sonra tahmin panelindeki `estimated_wear_um` alanını besler.

---

## 3. Train/Test Split Kuralı

Kesin kural:

```text
Aynı Set hem train hem test içinde bulunmamalı.
```

Yanlış:

```text
rows üzerinden random train_test_split
```

Doğru:

```text
Set bazlı split
```

Başlangıç split önerisi:

```text
train_sets: 1,2,3,4,5,6,7,8,9,10,11,12
val_sets:   13,14
test_sets:  15,16,17
```

Notlar:

- Set 13 şu an repoda kısmen çıkarılmış görünüyor; hızlı smoke test için kullanılabilir.
- Nihai eğitim için tüm 17 set görüntü dosyası canonical data root altına çıkarılmalı.
- Split seçimi class/wear dağılımı raporlandıktan sonra revize edilebilir.

---

## 4. Üretilecek Manifest Dosyaları

Manifestler kodun doğrudan okuyacağı temiz CSV'lerdir. `data/labels.csv` ham kaynak olarak kalır.

### 4.1 `data/manifests/image_anomaly_manifest.csv`

Kolonlar:

```text
image_path,set,image_id,image_datetime,wear,wear_bucket,anomaly_label,split
```

Örnek:

```text
image_path,set,image_id,image_datetime,wear,wear_bucket,anomaly_label,split
/data/.../Set1/images/xxx.jpg,1,0,2022-09-09 13:42:21.698185,30.0,normal,0,train
```

Kurallar:

- `image_path` absolute veya project-root relative tek formata normalize edilmeli.
- Dosya bulunamazsa satır manifest'e alınmamalı, eksik dosya raporuna yazılmalı.
- `45 < wear < 90` satırları başlangıçta `wear_bucket=mild` olarak işaretlenmeli; eğitim loader'ı isterse hariç tutmalı.

### 4.2 `data/manifests/image_wear_type_manifest.csv`

Kolonlar:

```text
image_path,set,image_id,image_datetime,wear,type_label,split
```

Kurallar:

- Boş `type` satırları başlangıçta çıkarılır veya `type_label=unknown` olarak sadece rapora alınır.
- `flank_wear+adhesion` => `combination` normalize edilir.

### 4.3 `reports/image_data_quality.md`

İçerik:

- Toplam label satırı
- Bulunan/bulunamayan image dosyası sayısı
- Set bazlı satır sayısı
- Split bazlı satır sayısı
- `wear` histogramı / bucket dağılımı
- `type` dağılımı
- Eksik type sayısı
- Örnek 10 path resolution sonucu

---

## 5. Image Model Eğitim Akışı

### Adım 1: Veri dosyalarını doğrula

Kontrol edilecekler:

```text
- data/labels.csv var mı?
- Tüm beklenen Set image klasörleri var mı?
- ImageFile path'leri gerçek dosyaya çözülebiliyor mu?
- type boşları kaç adet?
- wear değerleri numeric mi?
```

Beklenen çıktı:

```text
reports/image_data_quality.md
```

### Adım 2: Manifest üret

Script önerisi:

```text
server/scripts/build_image_manifests.py
```

Çıktılar:

```text
data/manifests/image_anomaly_manifest.csv
data/manifests/image_wear_type_manifest.csv
reports/image_data_quality.md
```

### Adım 3: Baseline image classifier çalıştır

İlk baseline için amaç model mimarisini kanıtlamak, SOTA yapmak değil.

Önerilen başlangıç:

```text
EfficientNet-B0 / ResNet18 / MobileNetV3
```

Task:

```text
binary anomaly classification
input: image_path
label: anomaly_label
```

Metrikler:

```text
AUROC
F1
precision
recall
confusion matrix
threshold bazlı recall
```

Çıktılar:

```text
models/image-anomaly-baseline/
reports/image_anomaly_baseline.md
reports/image_anomaly_confusion_matrix.png
```

### Adım 4: PatchCore / Anomalib denemesi

Amaç:

```text
normal/low_wear görüntülerle memory bank kurup high_wear görüntülerde anomali skoru üretmek
```

Train input:

```text
split=train AND anomaly_label=0
```

Validation/test input:

```text
split=val/test AND anomaly_label in {0,1}
```

Önemli:

- PatchCore train setine high_wear/anomaly görüntü sokulmamalı.
- Mild bucket başlangıçta train'e sokulmamalı.
- Set leakage kontrolü eğitimden önce otomatik yapılmalı.

Çıktılar:

```text
models/patchcore-image-anomaly/
reports/patchcore_image_anomaly.md
reports/patchcore_scores.csv
```

### Adım 5: Wear type classifier

Task:

```text
flank_wear vs adhesion vs combination
```

Input:

```text
data/manifests/image_wear_type_manifest.csv
```

Metrikler:

```text
macro F1
per-class precision/recall
confusion matrix
```

Çıktılar:

```text
models/wear-type-classifier/
reports/wear_type_classifier.md
reports/wear_type_confusion_matrix.png
```

### Adım 6: Inference script/API

Script:

```text
server/scripts/run_image_inference.py
```

Input:

```text
--image path/to/image.jpg
```

Output JSON:

```json
{
  "image_path": "...",
  "anomaly_score": 0.87,
  "anomaly_label": 1,
  "estimated_wear_um": 145.0,
  "wear_type": "flank_wear",
  "wear_type_probs": {
    "flank_wear": 0.87,
    "adhesion": 0.10,
    "combination": 0.03
  }
}
```

FastAPI endpoint hedefi:

```text
POST /api/inference/image
```

---

## 6. Çalıştırma Komutları — Hedef Taslak

Bu komutlar implementasyon sonrası çalışır hale getirilecek hedef komutlardır.

```bash
# 1. Veri kalite raporu + manifest üret
python server/scripts/build_image_manifests.py \
  --labels data/labels.csv \
  --data-root data \
  --fallback-root llm_docs \
  --out-dir data/manifests \
  --report reports/image_data_quality.md

# 2. Baseline binary classifier eğit
python server/scripts/train_image_anomaly_baseline.py \
  --manifest data/manifests/image_anomaly_manifest.csv \
  --out-dir models/image-anomaly-baseline \
  --report reports/image_anomaly_baseline.md

# 3. PatchCore / Anomalib eğit
python server/scripts/train_patchcore.py \
  --manifest data/manifests/image_anomaly_manifest.csv \
  --out-dir models/patchcore-image-anomaly \
  --report reports/patchcore_image_anomaly.md

# 4. Wear type classifier eğit
python server/scripts/train_wear_type_classifier.py \
  --manifest data/manifests/image_wear_type_manifest.csv \
  --out-dir models/wear-type-classifier \
  --report reports/wear_type_classifier.md

# 5. Tek görüntü inference
python server/scripts/run_image_inference.py \
  --image llm_docs/Set13/images/Test_0015_1_02_012_2023-03-16T09_26_06.353427.jpg \
  --model-dir models/patchcore-image-anomaly
```

---

## 7. Kabul Kriterleri

### Veri hazırlığı

- [ ] `data/labels.csv` okunuyor.
- [ ] En az bir image root üzerinden dosyalar çözülebiliyor.
- [ ] Eksik image path'leri raporlanıyor.
- [ ] Set bazlı split üretiliyor.
- [ ] Train/val/test arasında Set overlap yok.
- [ ] `data/manifests/image_anomaly_manifest.csv` oluşuyor.
- [ ] `data/manifests/image_wear_type_manifest.csv` oluşuyor.
- [ ] `reports/image_data_quality.md` oluşuyor.

### Eğitim

- [ ] Baseline model train komutu çalışıyor.
- [ ] PatchCore train komutu çalışıyor.
- [ ] Wear type classifier train komutu çalışıyor.
- [ ] Her eğitim sonunda rapor ve model artifact oluşuyor.
- [ ] Test metrikleri set bazlı split üstünden raporlanıyor.

### Inference

- [ ] Tek görüntü için JSON çıktı üretilebiliyor.
- [ ] JSON içinde `anomaly_score`, `estimated_wear_um`, `wear_type` alanları var.
- [ ] FastAPI inference endpoint'i bu çıktıyı dönebilecek formata sahip.

---

## 8. Sık Yapılacak Hatalar

- Row-level random split yapmak: leakage yaratır.
- PatchCore train setine anomali/high_wear görüntü koymak: model sınırını bozar.
- Boş `type` değerlerini fark etmeden classifier'a sokmak: label noise yaratır.
- `ImageFile` path'ini tek root'a göre varsaymak: mevcut repoda `MATWI/` prefix'i ile çıkarılmış klasör yapısı farklı olabilir.
- Sensör CSV'lerini image model input'u sanmak: v1.0'da sensör input değil, ayrı dashboard/veri kalite kanalıdır.

---

## 9. Phase Bağlantısı

Bu plan Roadmap Phase 2'nin detay alt planıdır.

Bağlı fazlar:

- Phase 1: image dosyaları, labels.csv, split ve veri kalite raporu hazırlanır.
- Phase 2: image anomaly model, PatchCore, wear type classifier ve inference script/API yapılır.
- Yedek parça krizi mock planı: `.planning/yedek-parca-krizi-mock-plan.md`; burada üretilen stok/ticket verisi image model eğitiminde label olarak kullanılmaz, yalnız inference/tahmin sonrası iş riski katmanını besler.
- Phase 4: model çıktıları dashboard anomali panelinde gösterilir.
- Phase 5: kritik anomali/tahmin çıktıları PUQ AI bildirim payload'ına eklenir.

---

*Son güncelleme: 2026-05-15 — image model eğitim/veri inceleme planı eklendi.*
