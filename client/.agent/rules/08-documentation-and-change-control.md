# Documentation & Change Control Rules

## Kesinlikle yapılacaklar
- Her faz sonrası gereksinimleri, out-of-scope maddelerini ve gerçekleşen kararları `.planning` belgeleriyle uyumlu tut.
- Üretilen veri/model/entegrasyon işleri için rapor yaz:
  - `reports/image_data_quality.md`
  - `reports/image_anomaly_baseline.md`
  - `reports/patchcore_image_anomaly.md`
  - `reports/wear_type_classifier.md`
  - `reports/mock_spare_parts_quality.md`
  - faza özel ek kalite/entegrasyon raporları
- Mock/simülasyon olan her şeyi UI, rapor ve dokümanda açıkça `mock`, `sentetik` veya `simülasyon` olarak etiketle.
- Out-of-scope kararlarını kod yorumlarında değil, plan/dokümantasyon seviyesinde görünür tut.
- Yeni karar mevcut planla çelişiyorsa önce plan çelişkisini çöz, sonra kodu değiştir.
- Dış servislerin bilinmeyen veya public olmayan API davranışlarında wrapper + config + hata mesajı ile ilerle; dokümana varsayımı yaz.
- Değişiklik sonrası ilgili test/rapor komutlarını çalıştır ve sonucu not et.

## Kesinlikle yapılmayacaklar
- MATWI gerçek verisi ile sentetik/mock yedek parça verisini dokümantasyonda karıştırma.
- Gerçek satın alma, gerçek ERP, gerçek supplier entegrasyonu varmış gibi metin yazma.
- Plan dışı teknoloji değişimini sessizce yapma.
- Faz veya gereksinim tamamlanmadıysa `done`/`validated` gibi kesin ifade kullanma.
- Rapor/artifact üretmeden model veya veri pipeline'ını tamam sayma.
- Sadece kod değiştirip `.planning` kararlarıyla uyumsuz yeni davranış bırakma.

## Dil ve isimlendirme
- Kullanıcı-facing dokümanlarda Türkçe tercih edilir.
- API/kolon/enum isimlerinde planlanan İngilizce snake_case değerleri koru.
- Risk seviyeleri ve status değerleri planla aynı kalmalı: `none`, `watch`, `at_risk`, `crisis`, `ready_for_review`, `approved` vb.
