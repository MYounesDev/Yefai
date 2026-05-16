# AI Services & Model Rules

## Kesinlikle yapılacaklar
- Görüntü anomalisi için Anomalib PatchCore yaklaşımını koru; few-shot/normal görüntülerle memory bank oluştur.
- Embedding için tek model olarak Jina CLIP v2 (`jinaai/jina-clip-v2`, 1024 dim, Türkçe destekli) kullan.
- RAG'de kullanıcı metnini Jina CLIP v2 text embedding ile aynı vektör uzayına taşı; pgvector top-k + metadata filtre ile context oluştur.
- NovaVision v1.0'da local Docker/localhost inference olarak ele alınmalı; bulut inference varsayma.
- NovaVision gerçek model hazır olmadan mock mode sözleşmesiyle endpointleri test edilebilir tut.
- NovaVision container düşerse Phase 2A lokal inference fallback'ına yönlen; ayrı bir cloud fallback icat etme.
- LLM provider'ı `.env` üzerinden seçilebilir yap (`gemini`/`claude` vb.); token/rate limit ve streaming SSE davranışını soyutla.
- PUQ AI bildirimleri webhook ile tetikle; async HTTP client, retry ve log mekanizması kullan.
- PUQ AI offline ise retry + log ve uygun platformda OS/native notification fallback yaklaşımını koru.
- Gerçek servis gerektiren testleri mock/marker ile ayır.

## Kesinlikle yapılmayacaklar
- TimesFM'i v1.0 sensör anomaly detection için ekleme; v1.1+ kapsamıdır.
- Jina CLIP v2 yerine Gemini Embedding/EmbeddingGemma gibi iki modele dönüş yapma; plan tek multimodal embedding modeli üzerine kuruludur.
- NovaVision'ı embedding sağlayıcısı gibi kullanma; NovaVision sadece CV/inference pipeline içindir.
- NovaVision public olmayan CLI/API komutlarını kesinmiş gibi kodda hardcode etme; wrapper + config + net hata mesajı kullan.
- Gerçek model, token veya container yokken live inference başarılıymış gibi raporlama.
- LLM live key yokken RAG live sonucunu gerçek kabul etme; mock provider kullan.
- PUQ AI webhook yokken Telegram/e-posta/SMS gönderildi iddiası yazma.

## Servis rolleri
- Anomalib/PatchCore: görüntü anomali skoru ve model artifact.
- Jina CLIP v2: görüntü + metin embedding, RAG ve arama.
- NovaVision local: deploy edilmiş Torch model ile local preprocessing/inference.
- LLM: RAG yanıt üretimi.
- PUQ AI: webhook tabanlı Telegram/e-posta/SMS/workflow otomasyonu.
