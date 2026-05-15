# labels.csv EDA Raporu

Kaynak: `/home/furkan/Projects/Yefai/data/labels.csv`

## Veri şekli

- Satır: 1803
- Kolon: 11
- Exact duplicate: 0
- ImageID/SensorID uyuşmayan satır: tüm satırlarda 1386; iki ID de mevcutken 1161
- Eksik değerler metadata/label kolonlarında mevcut: ImageName/ImageID/ImageDateTime/ImageFile 122, SensorName/SensorID/SensorDateTime/SensorFile 103, wear 140, type 135

## Kolon kalite özeti

| kolon | eksik | eksik_oranı | benzersiz |
| --- | --- | --- | --- |
| ImageName | 122 | 6.8% | 1680 |
| SensorName | 103 | 5.7% | 1700 |
| Set | 0 | 0.0% | 17 |
| ImageID | 122 | 6.8% | 152 |
| SensorID | 103 | 5.7% | 213 |
| wear | 140 | 7.8% | 28 |
| type | 135 | 7.5% | 3 |
| ImageDateTime | 122 | 6.8% | 1680 |
| SensorDateTime | 103 | 5.7% | 1700 |
| ImageFile | 122 | 6.8% | 1680 |
| SensorFile | 103 | 5.7% | 1700 |

## Sayısal özet

| kolon | count | min | q25 | median | mean | q75 | max | std |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Set | 1803 | 1.0 | 5.0 | 8.0 | 8.809 | 14.0 | 17.0 | 4.94 |
| ImageID | 1681 | 0.0 | 24.0 | 49.0 | 53.55 | 79.0 | 151.0 | 35.426 |
| SensorID | 1700 | 0.0 | 24.75 | 49.5 | 56.872 | 81.0 | 212.0 | 41.975 |
| wear | 1663 | 15.0 | 60.0 | 90.0 | 109.528 | 150.0 | 750.0 | 77.977 |

## Hedef/etiket dağılımları

### type
| type | adet | oran |
| --- | --- | --- |
| flank_wear | 1154 | 64.0% |
| flank_wear+adhesion | 335 | 18.6% |
| adhesion | 179 | 9.9% |
| <missing> | 135 | 7.5% |

### wear
| wear | adet | oran |
| --- | --- | --- |
| <missing> | 140 | 7.8% |
| 15.0 | 32 | 1.8% |
| 30.0 | 150 | 8.3% |
| 45.0 | 172 | 9.5% |
| 50.0 | 8 | 0.4% |
| 60.0 | 212 | 11.8% |
| 75.0 | 145 | 8.0% |
| 90.0 | 268 | 14.9% |
| 100.0 | 39 | 2.2% |
| 105.0 | 45 | 2.5% |
| 120.0 | 143 | 7.9% |
| 125.0 | 13 | 0.7% |
| 135.0 | 13 | 0.7% |
| 150.0 | 109 | 6.0% |
| 165.0 | 2 | 0.1% |
| 175.0 | 3 | 0.2% |
| 180.0 | 102 | 5.7% |
| 200.0 | 9 | 0.5% |
| 210.0 | 48 | 2.7% |
| 240.0 | 43 | 2.4% |
| 250.0 | 3 | 0.2% |
| 270.0 | 35 | 1.9% |
| 300.0 | 36 | 2.0% |
| 330.0 | 1 | 0.1% |
| 360.0 | 12 | 0.7% |
| 390.0 | 1 | 0.1% |
| 420.0 | 17 | 0.9% |
| 450.0 | 1 | 0.1% |
| 750.0 | 1 | 0.1% |

### Set
| Set | adet | oran |
| --- | --- | --- |
| 1 | 98 | 5.4% |
| 2 | 115 | 6.4% |
| 3 | 106 | 5.9% |
| 4 | 108 | 6.0% |
| 5 | 73 | 4.0% |
| 6 | 214 | 11.9% |
| 7 | 107 | 5.9% |
| 8 | 104 | 5.8% |
| 9 | 104 | 5.8% |
| 10 | 104 | 5.8% |
| 11 | 104 | 5.8% |
| 12 | 55 | 3.1% |
| 13 | 54 | 3.0% |
| 14 | 158 | 8.8% |
| 15 | 51 | 2.8% |
| 16 | 101 | 5.6% |
| 17 | 147 | 8.2% |

## Zaman ve dosya denetimi

- ImageDateTime aralığı: 2022-09-09 13:42:21.698185 → 2023-07-03 14:34:18.507821
- SensorDateTime aralığı: 2022-09-09 13:30:37.534347 → 2023-07-03 14:32:39.087120
- ImageDateTime - SensorDateTime dakika özeti: min=1.306, median=1.456, mean=4.290, max=3993.488
- `data/` altında var görünen ImageFile: 122/1803
- `data/` altında var görünen SensorFile: 103/1803
- proje kökü altında var görünen ImageFile: 122/1803
- proje kökü altında var görünen SensorFile: 103/1803

## Karar tablosu

| alan | bulgu | karar/aksiyon |
| --- | --- | --- |
| Problem contract | Her satır bir görüntü + sensör dosyası eşleşmesi gibi görünüyor; hedefler wear (ordinal/numeric aşınma seviyesi) ve type (aşınma tipi) olarak ele alınabilir. | Veri sahibiyle tahmin anında Image/Sensor dosyalarının ve label zamanlamasının kullanılabilirliğini doğrula. |
| Validation | 17 Set var; dosya adları ve zaman sırası Set içinde bağımlı olabilir. | Random split yerine önce Set bazlı veya zaman-sıralı holdout düşün; random split aynı deney koşullarını sızdırabilir. |
| Leakage | ImageID/SensorID, dosya adları ve timestamp alanları hedef üretim sürecini/sekansı kodlayabilir. | Modellemede ID/dosya adı/timestamp ham biçimde kullanılmamalı; yalnızca split/grup/denetim için tut. |
| Quality | Metadata/label eksikleri var: Image tarafında 122, Sensor tarafında 103, wear 140, type 135; exact duplicate=0. | Temel duplicate sorunu yok; eksik label/metadata satırları modelleme öncesi ayrıştırılmalı ve fiziksel dosya varlığı pipeline içinde doğrulanmalı. |
| Target | type dağılımı dengesiz: en büyük sınıf flank_wear=1154 satır. | Sınıflandırmada balanced accuracy/F1-macro raporla; regression için wear seviyelerini ordinal yapı olarak değerlendir. |

## Modelleme notları

- `wear` seviyeleri ayrık/ordinal görünüyor; regression, ordinal classification veya sınıflandırma olarak ayrı ayrı denenebilir.
- `type` çok sınıflı ve dengesiz; stratification tek başına yetmeyebilir, Set/time bağımlılığı öncelikli kontrol edilmeli.
- `ImageName`, `SensorName`, `ImageFile`, `SensorFile`, `ImageID`, `SensorID`, ham timestamp alanları leakage/proxy riski taşır; performans şişmesini önlemek için feature olarak değil audit/split metadata olarak kullanılmalı.
- Asıl sinyal muhtemelen görüntü ve sensör dosyalarının içeriğinde; bu dosya label tablosu tek başına daha çok manifest/metadata EDA'sıdır.

## Açık sorular

1. Tahmin görevi tam olarak hangisi: `wear`, `type`, ikisi birlikte mi?
2. Deployment sırasında sensör verisi, görüntü, timestamp ve Set bilgisi kullanılabilir mi?
3. `Set` deney/oturum/parti sınırı mı? Evetse validation group split olmalı.
