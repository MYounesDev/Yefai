# Yedek Parça Krizi Mock Planı — Yefai v1.0

> Amaç: Sunumdaki üçüncü problem olan **"Yedek Parça Krizi"**ni, MATWI veri setinde stok/BOM/satın alma verisi olmadığı halde, mevcut GSD planını bozmadan **sentetik/mock envanter + ticket + otomatik sipariş + alternatif tedarikçi katmanı** olarak eklemek.
> Bu katman model eğitim datasına karışmaz; anomali/tahmin çıktılarının üstüne iş kararı simülasyonu olarak bağlanır.
> v1.0 kapsamında: kriz tespiti, alarm, otomatik mock sipariş, alternatif tedarikçi önerme. Gerçek ERP entegrasyonu ve dinamik stok optimizasyonu v1.1+.

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
data/mock/suppliers.csv
data/mock/inventory_snapshots.csv
data/mock/part_tickets.csv
data/mock/purchase_orders.csv
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
| `auto_po_id` | Otomatik oluşturulan PO referansı (opsiyonel) |
| `recommended_supplier_id` | Önerilen alternatif tedarikçi (opsiyonel) |

### 3.4 `suppliers.csv`

| Kolon | Açıklama |
|---|---|
| `supplier_id` | Sentetik tedarikçi ID |
| `supplier_name` | Örn. KES-Tedarik A.Ş., GlobalTool GmbH |
| `part_id` | Tedarik ettiği parça |
| `is_primary` | Birincil tedarikçi mi (true/false) |
| `lead_time_days_p50` | Beklenen tedarik süresi |
| `lead_time_days_p90` | Kötümser tedarik süresi |
| `reliability_score` | 0-100 güvenilirlik |
| `unit_cost` | Bu tedarikçiden birim fiyat |
| `min_order_qty` | Minimum sipariş adedi |
| `in_stock_probability` | Stokta bulunma olasılığı (0-1) |

### 3.5 `purchase_orders.csv`

Otomatik sipariş simülasyonu ile oluşturulan, satın alma ekranına kadar gelen ama gerçekleştirilmeyen mock PO'lar.

| Kolon | Açıklama |
|---|---|
| `po_id` | Mock satın alma sipariş ID |
| `ticket_id` | Hangi ticket'tan tetiklendi |
| `part_id` | Sipariş edilen parça |
| `supplier_id` | Seçilen tedarikçi |
| `order_qty` | Sipariş adedi |
| `unit_cost` | Birim fiyat |
| `total_cost` | Toplam maliyet |
| `created_at` | PO oluşturulma zamanı |
| `expected_delivery` | Beklenen teslim tarihi |
| `status` | `draft`, `ready_for_review`, `approved` (manuel onay simülasyonu) |
| `urgency` | `normal`, `rush`, `critical` |
| `alternative_supplier_id` | Daha iyi lead time'lı alternatif varsa ID'si |

**Not:** v1.0'da PO `ready_for_review` durumunda satın alma ekranında gösterilir, manuel onay bekler. Gerçek satın alma işlemi yapılmaz. Bu demo sınırıdır.

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

## 5. Otomatik Sipariş Simülasyonu (v1.0)

Kriz tespit edildiğinde (`risk_level >= at_risk`), sistem otomatik olarak mock satın alma siparişi (PO) hazırlar. PO **satın alma ekranına kadar gelir, işlem manuel onay bekler** — gerçek satın alma yapılmaz.

### Tetikleme Kuralları

| Risk Seviyesi | Aksiyon |
|---|---|
| `crisis` (≥80) | Otomatik PO oluştur, `urgency=critical`, satın alma ekranında kırmızı vurgu |
| `at_risk` (60-79) | Otomatik PO oluştur, `urgency=rush` |
| `watch` (35-59) | PO önerisi hazırla ama otomatik oluşturma, dashboard'da "önerilen sipariş" olarak göster |
| `none` (<35) | İşlem yok |

### PO Oluşturma Akışı

```text
1. Kriz tespit → ticket.status = stockout, ticket.risk_level >= at_risk
2. Envanter kontrolü: on_hand < required_qty → stok açığı hesaplanır
3. Birincil tedarikçi seçilir (suppliers tablosundan is_primary=true)
4. PO oluşturulur: part_id, supplier_id, order_qty, unit_cost, total_cost
5. expected_delivery = now + supplier.lead_time_days_p90
6. PO status = ready_for_review
7. Ticket güncellenir: ticket.auto_po_id = po.po_id
8. Dashboard'da satın alma ekranında PO kartı gösterilir
9. PUQ AI bildirimi: "Kritik stok açığı — satın alma siparişi hazır, onay bekliyor"
```

### Satın Alma Ekranı (Dashboard)

PO `ready_for_review` durumunda dashboard'da gösterilecek alanlar:

- Parça adı, gerekli adet, birim fiyat, toplam maliyet
- Tedarikçi adı, lead time (p50/p90), güvenilirlik skoru
- Beklenen teslim tarihi vs ihtiyaç tarihi karşılaştırması
- "Alternatif tedarikçi" butonu (varsa)
- "Onayla" / "İptal" butonları (manuel — demo sınırı)

**Demo notu:** Onayla/İptal butonları mock çalışır. Onay → PO status `approved` olur, dashboard'da yeşil onay bildirimi gösterilir. Gerçek satın alma API çağrısı yapılmaz.

---

## 6. Alternatif Tedarikçi Önerme (v1.0)

Kriz durumunda birincil tedarikçinin lead time'ı kritik eşiğe yetişmiyorsa, sistem alternatif tedarikçileri tarar ve önerir.

### Alternatif Tarama Mantığı

```text
1. Kriz tespit edildi, birincil tedarikçi belirlendi
2. Eğer supplier.lead_time_days_p90 > (needed_by - now):
   → Birincil tedarikçi yetişemiyor
3. Aynı part_id için diğer supplier'lar taranır (is_primary=false)
4. Her alternatif için:
   - Teslim yetişme skoru = (needed_by - now) / supplier.lead_time_days_p90
   - Güvenilirlik × maliyet × stok olasılığı ile sıralama
5. En iyi alternatif dashboard'da ve bildirimde gösterilir
```

### Alternatif Skorlaması

```text
alt_supplier_score =
  0.40 × delivery_feasibility +     // yetişme olasılığı
  0.25 × reliability_score +         // güvenilirlik
  0.20 × cost_competitiveness +      // maliyet rekabeti
  0.15 × in_stock_probability        // stokta bulunma
```

### Dashboard Gösterimi

| Durum | Gösterim |
|---|---|
| Alternatif var, daha iyi lead time | Yeşil rozet: "Alternatif: XTedarik — 5 gün daha erken" |
| Alternatif var ama daha pahalı | Sarı rozet: "Alternatif mevcut ama %30 daha maliyetli" |
| Alternatif yok (tek tedarikçi) | Kırmızı rozet: "Tek kaynak — alternatif yok, kriz riski yüksek" |
| Alternatif var, lead time benzer | Gri rozet: "Alternatif var ama süre avantajı yok" |

### PUQ AI Bildirimi

Kriz bildirimine alternatif tedarikçi alanı eklenir:

```json
{
  "crisis_level": "critical",
  "part_id": "PT-042",
  "part_name": "Spindle Bearing XR-9",
  "on_hand": 0,
  "needed_by": "2026-05-17T02:00:00Z",
  "primary_supplier": {
    "name": "GlobalTool GmbH",
    "lead_time_p90_days": 21,
    "delivery_feasible": false
  },
  "alternative_supplier": {
    "name": "HızlıParça A.Ş.",
    "lead_time_p90_days": 5,
    "delivery_feasible": true,
    "cost_diff_pct": 15
  },
  "recommendation": "Alternatif tedarikçiye yönlendirme önerilir"
}
```

---

## 7. GSD Fazlarına Yerleştirme

**Yeni faz açılmayacak.** Plan mevcut fazlara dağıtılır.

### Phase 1 — Veri Altyapısı & Supabase

Ek görevler:

- Mock spare part generator script'i yazılır.
- `labels.csv` satırlarından `machine_id/tool_id` mock eşlemesi türetilir.
- `spare_parts_catalog`, `suppliers`, `inventory_snapshots`, `part_tickets`, `purchase_orders` tabloları Supabase şemasına eklenir.
- `reports/mock_spare_parts_quality.md` üretilir: kritik sınıf dağılımı, stok açığı dağılımı, ticket dağılımı, tedarikçi dağılımı.

Süre etkisi: **+1.5 gün** (suppliers + purchase_orders tabloları eklendi)

### Phase 2 — AI Inference Pipeline

Ek görevler:

- Inference çıktısına parça eşlemesi için `recommended_part_id` / `part_family` alanı eklenir.
- **Otomatik PO oluşturma servisi:** Kriz tespitinde mock PO hazırlayan FastAPI endpoint'i (`POST /api/spare-parts/auto-order`)
- **Alternatif tedarikçi tarama servisi:** Lead time yetişmeyen durumda alternatif supplier öneren endpoint (`GET /api/spare-parts/alternative-suppliers/{part_id}`)
- Model eğitimi değişmez; mock inventory label olarak kullanılmaz.

Süre etkisi: **+1 gün** (önceden 0.5 gündü)

### Phase 4 — Dashboard & Anomali Yönetimi

Ek görevler:

- Sunumdaki üçüncü kart için "Yedek Parça Krizi" paneli eklenir.
- Anomali detay panelinde stok durumu gösterilir: eldeki stok, siparişte, lead time, risk skoru.
- Kriz ticket listesi eklenir: `waiting_part`, `stockout`, `ordered`.
- **Satın alma ekranı:** `ready_for_review` durumundaki PO'ları listeleyen, onayla/iptal butonlu panel.
- **Alternatif tedarikçi paneli:** PO detayında alternatif supplier karşılaştırma tablosu (lead time, maliyet, güvenilirlik).
- Tahmin panelindeki `hours_to_critical`, inventory lead time ile karşılaştırılır.

Süre etkisi: **+2 gün** (önceden 1 gündü — satın alma ekranı + tedarikçi paneli eklendi)

### Phase 5 — Tauri + PUQ AI

Ek görevler:

- PUQ AI payload'a yedek parça alanları eklenir.
- `crisis` seviyesinde Telegram/e-posta mesajında "stok yok / tedarik süresi kritik" uyarısı + alternatif tedarikçi önerisi yer alır.
- **PO bildirimi:** "Satın alma siparişi hazır, onay bekliyor" mesajı + PO özeti.
- Offline fallback bildiriminde parça adı, beklenen geliş tarihi ve alternatif tedarikçi bilgisi gösterilir.

Süre etkisi: **+1 gün** (önceden 0.5 gündü — PO ve alternatif tedarikçi bildirim alanları eklendi)

Toplam ek süre: **~5.5 gün** (önceden ~3 gündü). Yeni faz açılmadığı için roadmap yapısı korunur.

---

## 8. Kabul Kriterleri

- [x] MATWI `labels.csv` değiştirilmeden mock parça verisi üretilebiliyor / backend mock catalog contract'ı MATWI label'larına dokunmadan çalışıyor.
- [x] `spare_parts_catalog`, `suppliers`, `inventory_snapshots`, `purchase_orders` contract'ları API/service katmanında mevcut.
- [ ] Mock kalite raporunda kritik sınıf, ticket dağılımları ve tedarikçi dağılımı görünüyor — ayrı data-quality raporu bu task'ta yeniden üretilmedi.
- [x] En az 3 risk seviyesi örneği üretilebiliyor: `watch`, `at_risk`, `crisis`.
- [x] `crisis` ve `at_risk` seviyesinde otomatik PO oluşturuluyor, `ready_for_review` durumunda API'den listeleniyor.
- [ ] Dashboard'da üçüncü problem kartı veriyle besleniyor — frontend scope bekliyor.
- [x] Bir kritik anomali için "parça stokta yok ve lead time yetişmiyor" senaryosu backend kriz skoru/API contract'ında gösterilebiliyor.
- [x] Birincil tedarikçi yetişemediğinde alternatif tedarikçi önerisi backend API'de ve PUQ AI template payload'ında gösteriliyor.
- [ ] Tek tedarikçili parça için "alternatif yok" uyarısı dashboard'da kırmızı rozet olarak görünüyor — frontend scope bekliyor.
- [ ] RAG chatbot "Hangi kritik parçalar stokta yok?" sorusuna mock inventory context'iyle cevap verebiliyor — Phase 3A/RAG entegrasyonu bekliyor.
- [ ] Satın alma ekranında PO detayı (parça, tedarikçi, maliyet, lead time, alternatif) gösteriliyor — frontend scope bekliyor.
- [x] PUQ AI webhook payload/template contract'ında yedek parça krizi ve PO bildirimi alanları var; live kanal gönderimi G3 gate'e bağlı.

### Uygulama Notu — 2026-05-17

Bu plan Phase 3B backend mock-mode kapsamına işlendi. Kod tarafında notification/spare-parts API contract'ları hazır; dashboard, satın alma ekranı ve RAG chatbot maddeleri ilgili frontend/Phase 3A kapsamına bırakıldı. Detay: `.planning/phases/03b-puqai-kriz/SUMMARY.md`.

---

## 9. Planı Bozmamak İçin Sınırlar

- Mock inventory verisi **model eğitim label'ı değildir**.
- Mock ticket verisi **MATWI gerçekliği gibi sunulmaz**; demo/simülasyon katmanı olarak adlandırılır.
- Mock PO'lar **gerçek satın alma yapmaz**; satın alma ekranında `ready_for_review` durumunda gösterilir, manuel onay simülasyonu yapılır.
- Alternatif tedarikçi önerisi **mock supplier verisine dayanır**; gerçek tedarikçi veritabanı yoktur.
- Phase 2 image anomaly başarı kriterleri değişmez.
- Sensör tabanlı TimesFM yine v1.1+ kapsamındadır.
- Gerçek ERP/satın alma entegrasyonu ve dinamik stok optimizasyonu v1.1+ kapsamındadır.

---

## 10. Demo Senaryosu (Güncel)

1. Görüntü akışında yüksek wear/anomali yakalanır.
2. Tahmin modülü "kritik eşiğe 16 saat" hesaplar.
3. Parça eşleme modülü gerekli parçayı bulur: `Insert Tip A-12`.
4. Inventory modülü kontrol eder:
   - `on_hand = 0`
   - `on_order = 1`
   - `lead_time_p90 = 21 gün` (birincil tedarikçi: GlobalTool GmbH)
   - `needed_by = 16 saat`
5. Sistem `crisis` ticket üretir.
6. **Otomatik PO** oluşturulur: `PO-2026-0042`, urgency=critical, status=`ready_for_review`.
7. Birincil tedarikçi yetişemiyor → **alternatif tedarikçi taranır**.
8. Alternatif bulunur: HızlıParça A.Ş. — lead_time_p90 = 5 gün, %15 daha pahalı.
9. Dashboard üçüncü kartta "Yedek Parça Krizi" kırmızı görünür.
10. **Satın alma ekranında** PO kartı: parça, tedarikçi karşılaştırması, maliyet, "Onayla/İptal" butonları.
11. PUQ AI Telegram/e-posta: "Üretim duruş riski — parça stokta yok. PO hazır, onay bekliyor. Alternatif tedarikçi: HızlıParça A.Ş. (5 gün)."
12. Operatör satın alma ekranında "Onayla"ya basar → PO `approved`, yeşil onay bildirimi. (Demo sonu — gerçek satın alma yapılmaz.)

---

*Son güncelleme: 2026-05-17 — Phase 3B backend mock-mode uygulama durumu, kabul kriterleri ve G3/frontend/RAG bekleyen kapsamları işlendi.*
