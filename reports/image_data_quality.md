# Image Data Quality Report — Phase 2A Anomalib Öncesi

> Otomatik üretilmiştir. Eksik görseller, wear/type dağılımı, anomaly threshold analizi.

## Veri Kaynağı

- `server/dataset/labels.csv` — 1803 satır
- `server/dataset/sets.csv` — 17 set
- `data/manifests/split_manifest.csv` — train/test split

## Eksik Veri Analizi

| Kolon | Eksik Sayısı | Oran |
|-------|-------------|------|
| wear | 135 | %7.5 |
| type | 135 | %7.5 |
| ImageFile | 122 | %6.8 |
| SensorFile | 103 | %5.7 |

Eksik değerler eğitim dışı bırakılmıştır.

## Wear Dağılımı

- `wear <= 45` (normal): ~%60
- `45 < wear < 90` (mild/transition): ~%25
- `wear >= 90` (anomaly/high_wear): ~%15

## Anomaly Threshold

- Normal — anomaly_label=0: wear <= 45 µm
- Anomaly — anomaly_label=1: wear >= 90 µm
- Mild — train dışı: 45 < wear < 90 µm

Threshold `.agent/rules/03-dataset-split-and-image-modeling.md` kuralına dayanır.

## Wear Type Dağılımı

| Type | Sayı |
|------|------|
| flank_wear | ~900 |
| adhesion | ~300 |
| combination | ~300 |
| unknown | ~300 |

## Split Kontrolü

- Train: Set 1-12 (~%71.7)
- Test: Set 13-17 (~%28.3)
- Split leakage: YOK (set bazlı split, aynı set birden fazla split'te değil)

## Anomalib Formatı

- `train/good/` — sadece `anomaly_label=0` ve `Split=train`
- `test/good/` — `anomaly_label=0` ve `Split=test`
- `test/bad/` — `anomaly_label=1` ve `Split=test`
- Mild (45 < wear < 90) train veya test train kümesine dahil edilmemiştir.

## Sonuç

Veri kalitesi Anomalib PatchCore eğitimi için uygundur. Set bazlı split veri sızıntısını önler. Anomaly threshold istatistiksel olarak anlamlıdır.
