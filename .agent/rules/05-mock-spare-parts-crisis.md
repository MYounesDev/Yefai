# Mock Spare Parts Crisis Rules

## Kesinlikle yapılacaklar
- Yedek parça krizi v1.0'da sentetik/mock iş kararı katmanıdır; MATWI gerçeği gibi sunulmaz.
- MATWI label'ları değiştirilmeden mock parça verisi üret.
- Üretilecek dosyalar:
  - `data/mock/spare_parts_catalog.csv`
  - `data/mock/suppliers.csv`
  - `data/mock/inventory_snapshots.csv`
  - `data/mock/part_tickets.csv`
  - `data/mock/purchase_orders.csv`
  - `reports/mock_spare_parts_quality.md`
- Mock generator için planlanan script yolunu koru veya bilinçli gerekçeyle güncelle:
  - `server/scripts/build_mock_spare_parts.py`
- Mock veride intermittent/lumpy spare-parts talep mantığını uygula:
  - criticality mix: A_vital %15, B_essential %35, C_desirable %50
  - demand pattern: intermittent %45, erratic %25, lumpy %20, smooth %10
  - lead time: criticality'ye göre değişken p50/p90
- Kriz skoru stok açığı, lead time farkı, kritiklik, supplier riski ve anomali şiddetini birlikte içermeli.
- Risk seviyeleri `none`, `watch`, `at_risk`, `crisis` olarak üret.
- `at_risk` ve `crisis` durumunda mock PO oluştur; status başlangıçta `ready_for_review` olmalı.
- `watch` durumunda PO önerisi yapılabilir, ancak otomatik PO oluşturulmaz.
- Birincil tedarikçi yetişemiyorsa alternatif supplier taraması yap; tek tedarikçide "alternatif yok" uyarısı üret.
- PUQ AI payload'ına yedek parça alanlarını ekle: `part_id`, `part_name`, `on_hand`, `needed_by`, `lead_time_days_p90`, `stockout_risk_score`, alternatif supplier bilgileri.

## Kesinlikle yapılmayacaklar
- Mock inventory verisini model eğitim label'ı yapma.
- Mock ticket verisini MATWI gerçekliği gibi sunma.
- Mock PO ile gerçek satın alma API çağrısı yapma.
- PO `approved` olsa bile bunu gerçek satın alma tamamlandı anlamına getirme; demo/simülasyon durumu olarak tut.
- Alternatif tedarikçi önerisini gerçek supplier database'e dayanıyor gibi gösterme.
- Gerçek ERP/MRO/CMMS entegrasyonu veya dinamik stok optimizasyonunu v1.0'a ekleme.
- Phase 2 image anomaly başarı kriterlerini yedek parça mock katmanı yüzünden değiştirme.

## Kabul sınırları
- En az `watch`, `at_risk`, `crisis` örnekleri üretilebilmeli.
- En az bir kritik senaryo: parça stokta yok + lead time yetişmiyor + alternatif supplier önerisi.
- Tek tedarikçili parça için açık "alternatif yok" durumu olmalı.
- RAG chatbot mock inventory context'iyle "Hangi kritik parçalar stokta yok?" sorusuna cevap verebilmeli.
