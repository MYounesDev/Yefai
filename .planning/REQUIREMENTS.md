# Requirements — Yefai Predictive Maintenance Platform

> Spesifik, test edilebilir, önceliklendirilmiş gereksinimler.
> Her gereksinimin bir kabul kriteri (UAT) vardır.

---

## Functional Requirements

### FR-1: Veri Seti Yönetimi

| ID | Gereksinim | Öncelik | UAT |
|----|-----------|---------|-----|
| FR-1.1 | 17 MATWI zip dosyası otomatik ayıklanır, labels.csv'den metadata parse edilir | P0 | Ayıklanan dosya sayısı = labels.csv'deki satır sayısı |
| FR-1.2 | Train/test split (%70/%30) set bazında yapılır, aynı set bölünmez | P0 | Test setindeki hiçbir Set ID train'de yok |
| FR-1.3 | Sensör CSV'leri parse edilir: Accelerometer, Acoustic, Force X/Y/Z, timestamp | P0 | Her sensör dosyası 6 kolon olarak okunur |
| FR-1.4 | Görüntüler ve sensör verisi timestamp ile eşleştirilir, senkronizasyon hataları loglanır | P1 | Eşleşen çift > %90, hatalar log'da |
| FR-1.5 | MATWI'de stok/BOM verisi olmadığı için mock yedek parça kataloğu, envanter snapshot'ı ve ticket datası üretilir | P0 | `spare_parts_catalog.csv`, `inventory_snapshots.csv`, `part_tickets.csv` ve kalite raporu oluşur |

### FR-2: AI Inference Engine (Görüntü Tabanlı)

| ID | Gereksinim | Öncelik | UAT |
|----|-----------|---------|-----|
| FR-2.1 | Anomalib (PatchCore) ile train setinde eğitim yapılır, Torch modeli export edilir | P0 | Train setinde normal örneklerle memory bank oluşturulur, model .pt olarak kaydedilir |
| FR-2.2 | Eğitilen Torch modeli NovaVision'a yüklenir, preprocessing + inference NovaVision'da çalışır | P0 | NovaVision API'den anomali skoru döner |
| FR-2.3 | Test setinde görüntü anomali tespiti: aşınma seviyesi > eşik olanlar işaretlenir | P0 | Eşik üstü görüntüler anomali olarak etiketlenir |
| FR-2.4 | Aşınma tipi sınıflandırması: Flank wear, Adhesive wear, Combination | P1 | En az %80 doğruluk |
| FR-2.5 | Sensör verisi dashboard'da canlı grafik olarak gösterilir, anomali tespitinde KULLANILMAZ | P0 | Sensör grafikleri 1 saniyede güncellenir |
| FR-2.6 | Jina CLIP v2 ile görüntü + metin embedding'i (tek model, aynı vektör uzayı) | P0 | Her görüntü için 1024 boyutlu vektör |

> **NOT:** Sensör tabanlı anomali tespiti (TimesFM 2.5) v1.1+ için ertelenmiştir. v1.0'da SADECE görüntü ile anomali tespiti yapılır.

### FR-3: Gerçek Zamanlı Veri Akışı

| ID | Gereksinim | Öncelik | UAT |
|----|-----------|---------|-----|
| FR-3.1 | Test verisi WebSocket üzerinden simüle gerçek zamanlı akış olarak gönderilir | P0 | 1 saniyede 1 veri noktası, gecikme < 100ms |
| FR-3.2 | Dashboard'da canlı sensör grafikleri (accelerometer, force, acoustic) | P0 | Grafikler 1 saniyede güncellenir |
| FR-3.3 | Kamera görüntüsü akışı (mock: sıralı görüntü gösterimi) | P1 | Anomali anında görüntü kırmızı çerçeve ile vurgulanır |
| FR-3.4 | Streaming agent: anomali tespitinde otonom aksiyon zinciri başlatır | P1 | Anomali → log → bildirim → öneri akışı otomatik |

### FR-4: RAG Chatbot

| ID | Gereksinim | Öncilik | UAT |
|----|-----------|---------|-----|
| FR-4.1 | Kullanıcı doğal dilde soru sorar: "Set 3'teki en yüksek aşınma ne zaman oldu?" | P0 | LLM doğru set/wear değerini döner |
| FR-4.2 | Chatbot yanıtları tıklanabilir ürün görselleri içerir | P0 | Görsele tıklandığında büyük görüntü modal'ı açılır |
| FR-4.3 | Sayısal veriler tablo formatında gösterilir | P0 | Tablo sortable, sayfalama var |
| FR-4.4 | RAG pipeline: soru → embedding → pgvector similarity search → context → LLM → yanıt | P0 | İlgili chunk'lar %90+ recall ile getirilir |
| FR-4.5 | Chatbot session'lar arası hafıza tutar (aynı session içinde) | P2 | Önceki soruya referans verilebilir |

### FR-5: Anomali Yönetimi & PUQ AI Bildirim

| ID | Gereksinim | Öncelik | UAT |
|----|-----------|---------|-----|
| FR-5.1 | Eşik aşılınca dashboard'da görsel/sesli uyarı | P0 | Kırmızı banner + ses, anomali detayları görünür |
| FR-5.2 | Uyarı detayları: zaman damgası, seri numarası, takım ID, aşınma tipi (flank/adhesive) | P0 | Tüm alanlar dolu |
| FR-5.3 | FastAPI → PUQ AI webhook: anomali tespit anında tetiklenir | P0 | Webhook payload'ı PUQ AI'ye ulaşır, HTTP 200 |
| FR-5.4 | PUQ AI Telegram workflow'u: anomali mesajı (seri no, görüntü, skor) | P0 | Telegram'dan test mesajı alınır |
| FR-5.5 | PUQ AI E-posta workflow'u: detaylı anomali raporu + görüntü eki | P1 | Test e-postası alınır |
| FR-5.6 | PUQ AI SMS workflow'u: kritik anomali → kısa mesaj | P2 | Test SMS'i alınır |
| FR-5.7 | PUQ AI raporlama workflow'u: günlük/haftalık özet rapor | P2 | Schedule ile otomatik rapor |
| FR-5.8 | Webhook retry mekanizması: PUQ AI offline ise kuyruğa al, tekrar dene | P1 | 3 retry, başarısız olursa log'a yaz |

### FR-6: Desktop Uygulama (Tauri)

| ID | Gereksinim | Öncilik | UAT |
|----|-----------|---------|-----|
| FR-6.1 | Tauri shell içinde Next.js frontend çalışır | P0 | `cargo tauri dev` ile açılır |
| FR-6.2 | Sistem tepsisinde (system tray) çalışır, minimize edilebilir | P1 | Tray ikonu görünür, sağ tık menüsü var |
| FR-6.3 | Native dosya sistemi erişimi: veri seti klasörü seçimi | P0 | Dosya seçici ile zip/klasör seçilebilir |
| FR-6.4 | Native bildirimler: anomali durumunda OS notification | P1 | macOS bildirim merkezinde görünür |
| FR-6.5 | Offline-first: FastAPI sunucusu başlatılmamışsa uyarı, local veri ile sınırlı çalışma | P2 | Sunucu yokken "Server offline" göstergesi |

### FR-7: Veritabanı & Embedding

| ID | Gereksinim | Öncelik | UAT |
|----|-----------|---------|-----|
| FR-7.1 | Supabase'de ilişkisel şema: sets, images, sensors, anomalies tabloları | P0 | Schema migration çalışır |
| FR-7.2 | pgvector eklentisi (Supabase built-in) ile embedding sütunu: image_embedding (1024-dim, MRL ile 64'e kısaltılabilir) | P0 | `SELECT * FROM images ORDER BY image_embedding <=> query_vector LIMIT 5` |
| FR-7.3 | Jina CLIP v2 ile görüntü + metin embedding'i — lokal, 865M parametre, 89 dil (Türkçe dahil) | P0 | 1663 görüntü için < 20 saniye |
| FR-7.4 | ~~Gemini Embedding 2~~ KALDIRILDI — Jina CLIP v2 tek model olarak hem görüntü hem metin embedding'i yapar | — | — |
| FR-7.5 | Hibrit arama: vektör similarity + metadata filtre (set, wear seviyesi, tarih) | P1 | "Set 5'teki flank wear görüntüleri" sorgusu |
| FR-7.6 | PUQ AI webhook log'ları Supabase'de saklanır (denetim için) | P2 | Her webhook call'u loglanır |
| FR-7.7 | Mock yedek parça tabloları: `spare_parts_catalog`, `inventory_snapshots`, `part_tickets` | P0 | Kriz senaryosu için parça, stok, lead time ve ticket sorgulanabilir |

### FR-8: Yedek Parça Krizi Mock Katmanı

| ID | Gereksinim | Öncelik | UAT |
|----|-----------|---------|-----|
| FR-8.1 | Anomali/tahmin çıktısı gerekli yedek parça veya parça ailesiyle eşleştirilir | P0 | Yüksek wear/anomali kaydında `recommended_part_id` dolu |
| FR-8.2 | Yedek parça talebi intermittent/lumpy dağılım varsayımıyla mock ticket'a dönüştürülür | P0 | Ticket dağılım raporunda `watch`, `at_risk`, `crisis` örnekleri var |
| FR-8.3 | Stok krizi skoru hesaplanır: stok açığı, lead time farkı, kritiklik, supplier riski, anomali şiddeti | P0 | Skor 0-100 ve risk seviyesi (`none/watch/at_risk/crisis`) döner |
| FR-8.4 | Dashboard'da “Yedek Parça Krizi” paneli gösterilir | P0 | Panelde parça adı, eldeki stok, siparişte, ihtiyaç tarihi, lead time, risk seviyesi görünür |
| FR-8.5 | RAG chatbot mock inventory üzerinde soru-cevap yapabilir | P1 | "Hangi kritik parçalar stokta yok?" sorusu tablo yanıtı döner |
| FR-8.6 | PUQ AI bildiriminde stok krizi alanları yer alır | P1 | Telegram/e-posta payload'ında parça, stok, lead time ve kriz skoru var |

---

## Non-Functional Requirements

| ID | Gereksinim | Hedef |
|----|-----------|-------|
| NFR-1 | Anomali tespit latency: sensör verisi geldikten sonra < 500ms | Performans |
| NFR-2 | Dashboard veri akışı: < 100ms gecikme | Performans |
| NFR-3 | RAG yanıt süresi: < 3 saniye | Performans |
| NFR-4 | Tauri uygulama boyutu: < 100MB | Kaynak |
| NFR-5 | Bellek kullanımı (boşta): < 200MB | Kaynak |
| NFR-6 | pgvector sorgu latency: < 50ms (10K vektör) | Performans |
| NFR-7 | Kod test coverage: > %70 (backend) | Kalite |
| NFR-8 | Tüm API endpoint'leri OpenAPI (Swagger) dokümanlı | Kalite |
| NFR-9 | macOS hedef platform (sonra Windows/Linux) | Platform |
| NFR-10 | AI modelleri offline çalışabilir (model dosyaları lokal) | Operasyon |

---

## Riskler & Mitigasyonlar

| Risk | Olasılık | Etki | Mitigasyon |
|------|---------|------|------------|
| MATWI veri setinde sync hataları (eksik sensör/görüntü) | Yüksek | Orta | Hata loglama, eksik veriyi atlama |
| Anomalib eğitim/inference süresi | Orta | Orta | GPU opsiyonu, batch inference |
| Tauri + Next.js entegrasyon sorunları | Orta | Yüksek | Önce pure Tauri + HTML testi, sonra Next.js |
| pgvector performansı büyük veride | Düşük | Orta | Supabase built-in pgvector, IVFFlat indexing |
| Real-time WebSocket kopmaları | Orta | Orta | Auto-reconnect, buffer |
| PUQ API downtime | Düşük | Yüksek | Webhook retry + log, kritik anomali için OS notification fallback |
| Jina CLIP v2 model yükleme/inference süresi | Düşük | Orta | ONNX export, batch inference, MRL boyut kısaltma |
| Mock yedek parça verisinin gerçek veri gibi algılanması | Orta | Orta | UI ve dokümantasyonda “mock/simülasyon” etiketi, gerçek ERP kapsamını v1.1+ olarak ayırma |
| Sentetik stok dağılımının aşırı yapay görünmesi | Orta | Orta | Intermittent/lumpy demand varsayımları, kritik sınıf dağılımı ve lead time değişkenliğiyle kalite raporu üretme |

---

*Last updated: 2026-05-15*
