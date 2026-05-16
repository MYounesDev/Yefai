# Data Storage, Supabase & pgvector Rules

## Kesinlikle yapılacaklar
- Ağır dosyaları local diskte tut: görüntüler ve sensör CSV'leri `data/MATWI/Set*/...` altında kalır.
- Supabase'i hafif metadata + pgvector store olarak kullan:
  - `sets`
  - `images` metadata + `file_path` + `image_embedding vector(1024)`
  - `anomalies`
  - mock yedek parça tabloları
  - webhook/log tabloları gerektiğinde
- Görüntü erişimi için `file_path` sakla; FastAPI local diskten serve eder.
- pgvector için Jina CLIP v2 1024 boyutlu embedding varsay; MRL ile 64/128/256 kısaltma sadece bilinçli optimizasyon olarak yapılır.
- HNSW index kullanmayı hedefle ve vektör aramayı metadata filtreleriyle hibrit SQL sorgu halinde tasarla.
- Supabase ücretsiz limitlerini korumak için yaklaşık veri boyutunu düşün; metadata/vektör dışı yüklemelerden kaçın.
- Environment değişkenlerini startup/lifespan sırasında doğrula.

## Kesinlikle yapılmayacaklar
- Görüntü BLOB'larını Supabase'e yükleme.
- Sensör CSV'lerini Supabase'e büyük raw array/blob olarak doldurma; v1.0'da local dosya ve özet/metadata yaklaşımı geçerlidir.
- Supabase'i Pinecone/Qdrant/Weaviate ile değiştirme; plan pgvector üzerine kuruludur.
- `file_path` yerine mutlak olarak sadece mevcut makineye kilitli, taşınamaz path formatına zorunlu bağımlılık yaratma; project-root relative veya açık normalize stratejisi kullan.
- pgvector boyutunu Jina CLIP v2 ile uyumsuz şekilde rastgele değiştirme.

## Beklenen tablolar / dosyalar
- `sets`, `images`, `anomalies`
- `spare_parts_catalog`, `suppliers`, `inventory_snapshots`, `part_tickets`, `purchase_orders`
- `webhook_logs` veya eşdeğer denetim kaydı
- `data/manifests/*`, `reports/*`
