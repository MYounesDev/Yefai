# Dataset Split & Image Modeling Rules

## Kesinlikle yapılacaklar
- MATWI ana label kaynağı olarak `data/labels.csv` kullan; ham label dosyasını değiştirme.
- Image path resolution yaparken birden fazla aday root kontrol et:
  1. `<project_root>/<ImageFile>`
  2. `<project_root>/data/<ImageFile>`
  3. `<project_root>/llm_docs/<ImageFile>`
  4. `<project_root>/llm_docs/<ImageFile without MATWI/>`
- Set bazlı train/val/test split üret; aynı `Set` asla birden fazla split'e girmemeli.
- Split leakage kontrolünü eğitimden önce otomatik çalıştır.
- Başlangıç split önerisini referans al, ancak dağılım raporuna göre revize edilebilir:
  - train: Set 1-12
  - val: Set 13-14
  - test: Set 15-17
- Binary anomaly label başlangıcı:
  - `wear <= 45` => normal/low_wear, `anomaly_label=0`
  - `wear >= 90` => anomaly/high_wear, `anomaly_label=1`
  - `45 < wear < 90` => mild/transition; başlangıçta train dışı veya yalnız val/test
- Wear type normalize et:
  - `flank_wear` => `flank_wear`
  - `adhesion` => `adhesion`
  - `flank_wear+adhesion` => `combination`
  - boş type => `unknown` veya eğitim dışı; raporla
- Manifest üret:
  - `data/manifests/image_anomaly_manifest.csv`
  - `data/manifests/image_wear_type_manifest.csv`
  - `reports/image_data_quality.md`
- PatchCore/Anomalib eğitiminde train input sadece `split=train AND anomaly_label=0` olmalı.
- Model çıktılarında en az `anomaly_score`, `estimated_wear_um`, `wear_type` JSON alanlarını hedefle.

## Kesinlikle yapılmayacaklar
- Row-level random `train_test_split` yapma; leakage yaratır.
- Aynı Set'i hem train hem test/val içine koyma.
- PatchCore train setine high_wear/anomaly görüntü koyma.
- Mild bucket'ı bilinçsizce normal train verisine dahil etme.
- Boş `type` değerlerini fark etmeden classifier'a sokma.
- `ImageFile` path'inin tek root altında kesin var olduğunu varsayma.
- Sensör CSV'lerini image model input'u yapma; v1.0'da sensörler image model eğitim girdisi değildir.
- Mock inventory/ticket/PO verisini model label'ı olarak kullanma.

## Metrikler ve raporlar
- Binary anomaly: AUROC, F1, precision, recall, confusion matrix, threshold bazlı recall.
- Wear type: macro F1, per-class precision/recall, confusion matrix.
- Her eğitim sonunda model artifact ve rapor üret.
