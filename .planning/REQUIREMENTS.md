# Requirements — Yefai Predictive Maintenance Platform

> Spesifik, test edilebilir, önceliklendirilmiş gereksinimler.
> Her gereksinimin bir kabul kriteri (UAT) vardır.

---

## Functional Requirements

### FR-1: Veri Seti Yönetimi

| ID | Gereksinim | Öncelik | UAT |
|----|-----------|---------|-----|
| FR-1.1 | 17 MATWI zip dosyası otomatik ayıklanır, labels.csv'den metadata parse edilir | P0 | Ayıklanan dosya sayısı = labels.csv'deki satır sayısı |
| FR-1.2 | Train/test split (%80/%20) set bazında yapılır, aynı set bölünmez | P0 | Test setindeki hiçbir Set ID train'de yok |
| FR-1.3 | Sensör CSV'leri parse edilir: Accelerometer, Acoustic, Force X/Y/Z, timestamp | P0 | Her sensör dosyası 6 kolon olarak okunur |
| FR-1.4 | Görüntüler ve sensör verisi timestamp ile eşleştirilir, senkronizasyon hataları loglanır | P1 | Eşleşen çift > %90, hatalar log'da |

### FR-2: AI Inference Engine

| ID | Gereksinim | Öncelik | UAT |
|----|-----------|---------|-----|
| FR-2.1 | TimesFM 2.5 ile zero-shot zaman serisi tahmini yapılır | P0 | Tahmin edilen değer ile gerçek değer karşılaştırılıp anomali skoru üretilir |
| FR-2.2 | Context window: son 50 adım → next-step tahmini | P0 | 50 adımdan az veri varsa uyarı, yoksa tahmin |
| FR-2.3 | Anomalib (PatchCore) ile görüntü üzerinde zero-shot anomali tespiti | P0 | Aşınma seviyesi > eşik olan görüntüler işaretlenir |
| FR-2.4 | Görüntü ve sensör anomali skorları birleştirilir (füzyon) | P1 | Birleşik anomali skoru 0-1 arası, eşik konfigüre edilebilir |
| FR-2.5 | CLIP/SigLIP ile multimodal embedding üretilir (görüntü + metin) | P0 | Her görüntü için 512/768 boyutlu vektör |

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
| FR-7.1 | PostgreSQL'de ilişkisel şema: sets, images, sensors, anomalies tabloları | P0 | Schema migration çalışır |
| FR-7.2 | pgvector eklentisi ile embedding sütunları: text_embedding (768-dim), multimodal_embedding (768-dim) | P0 | `SELECT * FROM images ORDER BY embedding <=> query_vector LIMIT 5` |
| FR-7.3 | EmbeddingGemma 300M ile metin embedding'leri (metadata, label, açıklama) — lokal | P0 | 1663 kayıt için < 2 dakika |
| FR-7.4 | Gemini Embedding 2 ile multimodal embedding (görüntü + akustik) — API | P0 | Toplu embedding, rate-limit yönetimi |
| FR-7.5 | Hibrit arama: vektör similarity + metadata filtre (set, wear seviyesi, tarih) | P1 | "Set 5'teki flank wear görüntüleri" sorgusu |
| FR-7.6 | PUQ AI webhook log'ları PostgreSQL'de saklanır (denetim için) | P2 | Her webhook call'u loglanır |

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
| TimesFM 2.5 model boyutu/inference süresi | Orta | Yüksek | ONNX quantized versiyonu, GPU opsiyonu |
| Tauri + Next.js entegrasyon sorunları | Orta | Yüksek | Önce pure Tauri + HTML testi, sonra Next.js |
| pgvector performansı büyük veride | Düşük | Orta | IVFFlat indexing, benchmark testi |
| Real-time WebSocket kopmaları | Orta | Orta | Auto-reconnect, buffer |
| PUQ API downtime | Düşük | Yüksek | Webhook retry + log, kritik anomali için OS notification fallback |
| Gemini Embedding 2 API rate limit | Orta | Düşük | Toplu embedding'i zamana yay, lokal EmbeddingGemma fallback |

---

*Last updated: 2026-05-15*
