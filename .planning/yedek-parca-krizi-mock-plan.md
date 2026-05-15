# Yedek Parça Krizi Mock Planı — Yefai v1.0

> Amaç: Sunumdaki üçüncü problem olan **“Yedek Parça Krizi”**ni, MATWI veri setinde stok/BOM/satın alma verisi olmadığı halde, mevcut GSD planını bozmadan **sentetik/mock envanter + ticket katmanı** olarak eklemek.
> Bu katman model eğitim datasına karışmaz; anomali/tahmin çıktılarının üstüne iş kararı simülasyonu olarak bağlanır.

---

## 1. Problem ve Veri Gerçeği

MATWI veri setinde mevcut olan ana alanlar:

- Görüntü ve sensör dosyası referansları
- `wear` aşınma seviyesi
- `type` aşınma tipi
- `Set`, timestamp ve dosya metadata’sı

MATWI’de olmayan fakat “Yedek Parça Krizi” için gereken alanlar:

- Parça kataloğu / BOM: `part_id`, `part_name`, uyumlu takım/makine
- Stok: `on_hand`, `reserved`, `on_order`
- Tedarik: `lead_time_days`, supplier sayısı, güvenilirlik
- Talep/ticket geçmişi: bakım emri, parça tüketimi, sipariş durumu

**Karar:** v1.0’da bu eksik alanlar `mock_spare_parts`, `mock_inventory_snapshots` ve `mock_part_tickets` olarak sentetik üretilecek. MATWI label’ları değiştirilmeyecek.

---

## 2. Araştırma Özeti ve Dağılım Varsayımları

Araştırma bulguları:

- Yedek parça talebi klasik düzenli ürün talebinden farklıdır; genelde **slow-moving, intermittent, erratic/lumpy** davranır. Bu yüzden normal dağılım varsayımı uygun değildir.
- Literatürde yedek parça talebi için **Poisson tabanlı dağılımlar**, özellikle **compound Poisson / negative binomial** yaklaşımları sık kullanılır.
- Kritik parça yönetiminde yalnız talep miktarı değil; ekipman kritiklik seviyesi, arıza olasılığı, ikmal süresi, supplier sayısı, teknik spesifikasyon erişimi ve bakım tipi birlikte değerlendirilir.
- Envanter kritikliğinde lead time, target service level, warehouse/BOM uygunluğu ve work order önceliği gibi pratik değişkenler de gerekir.

Kaynak dayanakları:

- Turrini & Meissner, “Spare parts inventory management: New evidence from distribution fitting” — spare parts demand için Poisson tabanlı dağılımlar ve lumpy/intermittent talep.
- Snyder vd., “Forecasting the intermittent demand for slow-moving inventories” — Poisson, negative binomial ve hurdle/zero-inflated yaklaşımlar.
- Molenaers vd., “Criticality classification of spare parts: A case study” — ekipman kritiği, failure probability, replenishment time, supplier sayısı gibi çok kriterli kritiklik.
- IBM MRO criticality rehberi — lead time, supplier, warehouse, BOM, service level, work order priority gibi operasyonel sorular.

### v1.0 Mock Dağılım Tasarımı

Bu oranlar gerçek veri iddiası değildir; araştırma bulgularına uyumlu, demo için kontrollü varsayımlardır.

| Alan | Mock dağılım / kural | Neden |
|---|---|---|
| SKU kritikliği | A/Vital %15, B/Essential %35, C/Desirable %50 | Az sayıda kritik SKU’nun yüksek operasyon etkisi olması |
| Talep paterni | Intermittent %45, erratic %25, lumpy %20, smooth %10 | Yedek parçada sıfır talep dönemleri ve ani sıçramalar beklenir |
| Talep olayı | Bernoulli + anomaly/tahmin skoru ile ağırlıklandırma | Talep çoğu zaman oluşmaz; kritik aşınma görünce olasılık artar |
| Talep adedi | Compound Poisson / Negative Binomial; çoğunluk 1, nadiren 2-4 | Tek arızada 1 parça sık, toplu değişim nadir |
| Lead time | Kritik sınıfa göre triangular/lognormal: A daha uzun ve değişken | Kritik/OEM parçalar daha uzun tedarik süresine sahip olabilir |
| Stok seviyesi | Criticality + service level hedefinden reorder point | Krizi stok yokluğu + ikmal gecikmesi üretir |
| Supplier riski | Supplier sayısı 1-3; tek supplier daha riskli | Tek kaynaklı parçada kriz olasılığı artar |

Başlangıç parametreleri:

```yaml
criticality_mix:
  A_vital: 0.15
  B_essential: 0.35
  C_desirable: 0.50

demand_pattern_mix:
  intermittent: 0.45
  erratic: 0.25
  lumpy: 0.20
  smooth: 0.10

lead_time_days:
  A_vital: triangular(min=14, mode=35, max=90)
  B_essential: triangular(min=7, mode=21, max=45)
  C_desirable: triangular(min=2, mode=10, max=30)

target_service_level:
  A_vital: 0.95
  B_essential: 0.90
  C_desirable: 0.80
```

---

## 3. Üretilecek Mock Veri Dosyaları

Mock üretim script’i:

```text
server/scripts/build_mock_spare_parts.py
```

Girdiler:

```text
server/dataset/labels.csv
reports/labels_eda_summary.json veya labels.csv üzerinden yeniden EDA
```

Çıktılar:

```text
data/mock/spare_parts_catalog.csv
data/mock/inventory_snapshots.csv
data/mock/part_tickets.csv
reports/mock_spare_parts_quality.md
```

### 3.1 `spare_parts_catalog.csv`

| Kolon | Açıklama |
|---|---|
| `part_id` | Sentetik parça ID |
| `part_name` | Örn. insert, tool holder, spindle bearing, coolant nozzle |
| `compatible_wear_type` | `flank_wear`, `adhesion`, `combination`, `any` |
| `criticality_class` | `A_vital`, `B_essential`, `C_desirable` |
| `abc_class` | A/B/C maliyet-kritiklik sınıfı |
| `supplier_count` | 1-3 |
| `lead_time_days_p50` | Beklenen tedarik süresi |
| `lead_time_days_p90` | Kötümser tedarik süresi |
| `unit_cost` | Mock maliyet |
| `service_level_target` | Kritikliğe göre hedef |

### 3.2 `inventory_snapshots.csv`

| Kolon | Açıklama |
|---|---|
| `snapshot_date` | Günlük stok anı |
| `part_id` | Parça |
| `on_hand` | Eldeki stok |
| `reserved_qty` | Açık ticket’lara rezerve |
| `on_order_qty` | Siparişte |
| `reorder_point` | Yeniden sipariş eşiği |
| `safety_stock` | Güvenlik stoku |
| `inventory_position` | `on_hand + on_order - reserved_qty` |

### 3.3 `part_tickets.csv`

| Kolon | Açıklama |
|---|---|
| `ticket_id` | Mock bakım/satın alma ticket ID |
| `source_label_row_id` | MATWI satır referansı |
| `set` | MATWI Set |
| `machine_id` | Mock makine |
| `tool_id` | Mock takım |
| `part_id` | Talep edilen parça |
| `required_qty` | 1-4 |
| `needed_by` | Tahmini kritik zamana göre ihtiyaç tarihi |
| `ticket_type` | `replacement`, `purchase_request`, `stockout_escalation` |
| `status` | `planned`, `waiting_part`, `ordered`, `stockout`, `closed` |
| `risk_level` | `none`, `watch`, `at_risk`, `crisis` |
| `stockout_risk_score` | 0-100 |

---

## 4. Kriz Skoru

Kriz, yalnızca “aşınma var” demek değildir. Kriz için parça ihtiyacı + stok/tedarik açığı birlikte değerlendirilir.

### Türetilen zamanlar

```text
needed_by = anomaly_time + hours_to_critical
expected_replenishment_date = today + lead_time_days_p90
lead_time_gap_days = expected_replenishment_date - needed_by
```

### Risk skoru

```text
stockout_risk_score =
  0.35 * shortage_probability +
  0.25 * lead_time_gap_score +
  0.20 * criticality_score +
  0.10 * supplier_risk_score +
  0.10 * anomaly_severity_score
```

### Risk seviyeleri

| Seviye | Kural |
|---|---|
| `none` | Skor < 35 veya stok yeterli |
| `watch` | 35-59; stok düşük ama kritik tarih yakın değil |
| `at_risk` | 60-79; ihtiyaç tarihi lead time içinde |
| `crisis` | >= 80 veya `on_hand - reserved < required_qty` ve `needed_by < replenishment_p90` |

---

## 5. GSD Fazlarına Yerleştirme

**Yeni faz açılmayacak.** Plan mevcut fazlara dağıtılır.

### Phase 1 — Veri Altyapısı & Supabase

Ek görevler:

- Mock spare part generator script’i yazılır.
- `labels.csv` satırlarından `machine_id/tool_id` mock eşlemesi türetilir.
- `spare_parts_catalog`, `inventory_snapshots`, `part_tickets` tabloları Supabase şemasına eklenir.
- `reports/mock_spare_parts_quality.md` üretilir: kritik sınıf dağılımı, stok açığı dağılımı, ticket dağılımı.

Süre etkisi: **+1 gün**

### Phase 2 — AI Inference Pipeline

Ek görev:

- Inference çıktısına parça eşlemesi için `recommended_part_id` / `part_family` alanı opsiyonel eklenir.
- Model eğitimi değişmez; mock inventory label olarak kullanılmaz.

Süre etkisi: **+0.5 gün**

### Phase 4 — Dashboard & Anomali Yönetimi

Ek görevler:

- Sunumdaki üçüncü kart için “Yedek Parça Krizi” paneli eklenir.
- Anomali detay panelinde stok durumu gösterilir: eldeki stok, siparişte, lead time, risk skoru.
- Kriz ticket listesi eklenir: `waiting_part`, `stockout`, `ordered`.
- Tahmin panelindeki `hours_to_critical`, inventory lead time ile karşılaştırılır.

Süre etkisi: **+1 gün**

### Phase 5 — Tauri + PUQ AI

Ek görevler:

- PUQ AI payload’a yedek parça alanları eklenir.
- `crisis` seviyesinde Telegram/e-posta mesajında “stok yok / tedarik süresi kritik” uyarısı yer alır.
- Offline fallback bildiriminde parça adı ve beklenen geliş tarihi gösterilir.

Süre etkisi: **+0.5 gün**

Toplam ek süre: **~3 gün**. Yeni faz açılmadığı için roadmap yapısı korunur.

---

## 6. Kabul Kriterleri

- [ ] MATWI `labels.csv` değiştirilmeden mock parça verisi üretilebiliyor.
- [ ] `spare_parts_catalog.csv`, `inventory_snapshots.csv`, `part_tickets.csv` oluşuyor.
- [ ] Mock kalite raporunda kritik sınıf ve ticket dağılımları görünüyor.
- [ ] En az 3 risk seviyesi örneği üretilebiliyor: `watch`, `at_risk`, `crisis`.
- [ ] Dashboard’da üçüncü problem kartı veriyle besleniyor.
- [ ] Bir kritik anomali için “parça stokta yok ve lead time yetişmiyor” senaryosu gösterilebiliyor.
- [ ] RAG chatbot “Hangi kritik parçalar stokta yok?” sorusuna mock inventory context’iyle cevap verebiliyor.
- [ ] PUQ AI webhook payload’ında `part_id`, `part_name`, `on_hand`, `needed_by`, `lead_time_days_p90`, `stockout_risk_score` alanları var.

---

## 7. Planı Bozmamak İçin Sınırlar

- Mock inventory verisi **model eğitim label’ı değildir**.
- Mock ticket verisi **MATWI gerçekliği gibi sunulmaz**; demo/simülasyon katmanı olarak adlandırılır.
- Phase 2 image anomaly başarı kriterleri değişmez.
- Sensör tabanlı TimesFM yine v1.1+ kapsamındadır.
- ERP/satın alma entegrasyonu v1.0 dışıdır; sadece mock ticket ve bildirim vardır.

---

## 8. Demo Senaryosu

1. Görüntü akışında yüksek wear/anomali yakalanır.
2. Tahmin modülü “kritik eşiğe 16 saat” hesaplar.
3. Parça eşleme modülü gerekli parçayı bulur: `Insert Tip A-12`.
4. Inventory modülü kontrol eder:
   - `on_hand = 0`
   - `on_order = 1`
   - `lead_time_p90 = 21 gün`
   - `needed_by = 16 saat`
5. Sistem `crisis` ticket üretir.
6. Dashboard üçüncü kartta “Yedek Parça Krizi” kırmızı görünür.
7. PUQ AI Telegram/e-posta: “Üretim duruş riski — parça stokta yok, tedarik tarihi kritik eşiği geçiyor.”

---

*Son güncelleme: 2026-05-16 — yedek parça krizi mock katmanı araştırma ve dağılım planı eklendi.*
