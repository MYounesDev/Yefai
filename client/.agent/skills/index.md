# Yefai Skill Index

Bu dosya `.planning/phases/*/PLAN.md` dosyalarına göre, ilgili fazı uygularken `/home/furkan/Projects/Yefai/.agent/skills` altındaki hangi proje skillerinin kullanılacağını belirtir.

## Kullanım kuralı

- Bir faz üzerinde çalışmaya başlamadan önce bu index'te ilgili `PLAN.md` satırını bul.
- `Zorunlu skill'ler` bölümündeki tüm skill'leri oku/uygula.
- `Duruma bağlı skill'ler` yalnızca ilgili alt görev varsa kullanılmalı.
- Kod yazımı yapılan her fazda `.agent/rules` altındaki kurallar da bağlayıcıdır.
- Plan ile skill çelişirse önce `.planning` kapsamı ve `.agent/rules` kararları geçerlidir; skill sadece uygulama yöntemi sağlar.

## Global skill'ler

Aşağıdaki skill'ler çoğu fazda ortak kullanılmalıdır:

| Skill | Ne zaman kullanılır |
|---|---|
| `graphify` | Kod tabanı/doküman ilişkisini anlamak, mevcut modülleri seçmek, değişiklik sonrası graphify güncellemek için. |
| `karpathy-guidelines` | Her fazda LLM kodlama hatalarını azaltmak, varsayımları görünür kılmak, basit/surgical değişiklik yapmak ve over-engineering önlemek için. Path: `andrej-karpathy-skills-main/skills/karpathy-guidelines/SKILL.md`. |
| `sade-surdurulebilir-mimari` | Mimari sınırlar, sadelik, sürdürülebilir modül ayrımı ve over-engineering kontrolü için. |
| `yazilim-prensipleri` | SOLID, DRY, KISS, YAGNI ve tasarım kalıpları açısından kod/plan kontrolü için. |
| `python-clean-code` | Python kodu yazılan, düzenlenen veya review edilen her fazda. |
| `python-pytest-ops` | pytest, fixture, mock, marker, coverage ve test organizasyonu gereken her fazda. |
| `software-testing-tdd-architecture` | Test stratejisi, unit/integration/contract/E2E ayrımı ve kalite mimarisi için. |
| `python-observability` | Logging, hata izleme, structured log ve operasyonel görünürlük gereken servislerde. |

---

## PLAN.md -> kullanılacak skill eşlemesi

### `.planning/phases/01-veri-altyapisi/PLAN.md`

Faz: Veri Altyapısı & Supabase Setup

Kapsam özeti:
- MATWI zip ayıklama, labels/sets/sensör parse.
- Set bazlı train/test split.
- Supabase hafif metadata + pgvector şema.
- Local dosya sistemi stratejisi.
- Mock yedek parça verisi ve kalite raporu.
- FastAPI proje iskeleti.

Zorunlu skill'ler:
- `graphify`
- `karpathy-guidelines` (`andrej-karpathy-skills-main/skills/karpathy-guidelines/SKILL.md`)
- `data-exploration`
- `exploratory-data-analysis`
- `data-analyst`
- `python-expert`
- `python-clean-code`
- `python-design-modularity`
- `python-fastapi-development`
- `python-pytest-ops`
- `software-testing-tdd-architecture`
- `sade-surdurulebilir-mimari`
- `yazilim-prensipleri`

Duruma bağlı skill'ler:
- `data-visualization` — veri kalite raporunda histogram/grafik üretilecekse.
- `data-storytelling` — `reports/image_data_quality.md` veya mock veri kalite raporu paydaş/demoya uygun yazılacaksa.
- `python-observability` — ETL/log/hata raporlama altyapısı ekleniyorsa.
- `api-testing-patterns` — FastAPI scaffold endpoint'leri için contract/API testleri yazılacaksa.

Özel notlar:
- Row-level random split yapılmaz; Set bazlı split zorunludur.
- Görüntü/sensör dosyaları Supabase'e BLOB olarak yüklenmez.
- Mock spare-parts verisi gerçek veri gibi sunulmaz.

---

### `.planning/phases/02a-anomalib-embedding/PLAN.md`

Faz: Anomalib Training & Embedding Pipeline

Kapsam özeti:
- Anomalib PatchCore eğitimi.
- Model export `.pt`.
- Test setinde lokal inference.
- Jina CLIP v2 embedding üretimi.
- pgvector'e embedding yazma.
- Anomalib ve embedding FastAPI endpoint'leri.

Zorunlu skill'ler:
- `graphify`
- `karpathy-guidelines` (`andrej-karpathy-skills-main/skills/karpathy-guidelines/SKILL.md`)
- `dl-image-preprocessing`
- `ml-training-error-prevention`
- `ml-reproducibility-seed-control`
- `data-scientist`
- `python-expert`
- `python-clean-code`
- `python-design-modularity`
- `python-fastapi-development`
- `python-pytest-ops`
- `software-testing-tdd-architecture`
- `sade-surdurulebilir-mimari`

Duruma bağlı skill'ler:
- `data-exploration` — manifest, label dağılımı ve split kalitesi tekrar incelenecekse.
- `data-visualization` — confusion matrix, skor dağılımı, metrik grafikleri üretilecekse.
- `data-storytelling` — model raporları karar vericiye anlatılacak şekilde yazılacaksa.
- `python-observability` — training/inference job logging ve status takibi eklenecekse.
- `api-testing-patterns` — `/api/anomalib/*` ve `/api/embeddings/*` endpoint testleri yazılacaksa.

Özel notlar:
- PatchCore train setine anomaly/high_wear görüntü sokulmaz.
- Mild bucket bilinçsizce normal train verisine dahil edilmez.
- Sensör CSV'leri image model input'u değildir.
- Jina CLIP v2 tek multimodal embedding modeli olarak korunur.

---

### `.planning/phases/02b-novavision-inference/PLAN.md`

Faz: NovaVision Local Inference Pipeline

Kapsam özeti:
- NovaVision CLI wrapper.
- Local Docker container lifecycle.
- Model deploy pipeline.
- Localhost REST inference client.
- Model gelene kadar mock mode.
- NovaVision FastAPI endpoint'leri.

Zorunlu skill'ler:
- `graphify`
- `karpathy-guidelines` (`andrej-karpathy-skills-main/skills/karpathy-guidelines/SKILL.md`)
- `docker-patterns`
- `python-expert`
- `python-clean-code`
- `python-design-modularity`
- `python-fastapi-development`
- `python-pytest-ops`
- `api-testing-patterns`
- `software-testing-tdd-architecture`
- `python-observability`
- `sade-surdurulebilir-mimari`

Duruma bağlı skill'ler:
- `ml-training-error-prevention` — model deploy/inference artifact doğrulaması yapılacaksa.
- `dl-image-preprocessing` — NovaVision'a gönderilecek görüntü preprocessing contract'ı netleştirilecekse.
- `github-actions-cicd-architecture` — Docker/NovaVision mock testleri CI'a eklenecekse.
- `corporate-git-ci-standards` — faz işleri atomic commit/branch planına bölünecekse.

Özel notlar:
- NovaVision v1.0'da local Docker/localhost inference'tır; cloud inference varsayılmaz.
- Gerçek CLI/API public değilse wrapper + config + net hata mesajı yazılır.
- Model veya container yokken live başarı iddiası yapılmaz; mock mode açıkça ayrılır.

---

### `.planning/phases/02c-gelecek-tahmini/PLAN.md`

Faz: Gelecek Tahmini / Wear Prediction Engine

Kapsam özeti:
- Anomalib skorundan tahmini wear µm kalibrasyonu.
- Aşınma hızı hesaplama.
- Kritik eşiğe kalan süre.
- 3 senaryolu projeksiyon.
- `anomalies` tablosuna tahmin alanları.
- Prediction API endpoint'leri.
- Phase 3B kriz skoru entegrasyon noktası.

Zorunlu skill'ler:
- `graphify`
- `karpathy-guidelines` (`andrej-karpathy-skills-main/skills/karpathy-guidelines/SKILL.md`)
- `data-scientist`
- `data-analyst`
- `data-exploration`
- `python-expert`
- `python-clean-code`
- `python-design-modularity`
- `python-fastapi-development`
- `python-pytest-ops`
- `software-testing-tdd-architecture`
- `sade-surdurulebilir-mimari`

Duruma bağlı skill'ler:
- `data-visualization` — projeksiyon/trend grafikleri veya rapor görselleri üretilecekse.
- `data-storytelling` — tahmin sonuçları demo/rapor diliyle anlatılacaksa.
- `ml-reproducibility-seed-control` — stochastic simülasyon/kalibrasyon denemeleri eklenecekse.
- `python-observability` — prediction recalculation job logging ve hata izleme eklenecekse.
- `api-testing-patterns` — `/api/predictions/*` contract/integration testleri yazılacaksa.

Özel notlar:
- Bu faz backend-only'dir; grafik/frontend UI yapılmaz.
- Tahmin hassas garanti değil, trend göstergesi olarak ele alınır.
- `hours_to_critical` Phase 3B'deki lead time/kriz karşılaştırmasını besler.

---

### `.planning/phases/03a-rag-pipeline/PLAN.md`

Faz: RAG Pipeline

Kapsam özeti:
- Kullanıcı sorusunu Jina CLIP v2 text embedding'e çevirme.
- pgvector similarity + SQL metadata filtreli hibrit arama.
- Context assembly: görüntü, metadata, opsiyonel sensör özeti.
- LLM provider abstraction.
- Streaming SSE chat endpoint'i.
- Chat session yönetimi.

Zorunlu skill'ler:
- `graphify`
- `karpathy-guidelines` (`andrej-karpathy-skills-main/skills/karpathy-guidelines/SKILL.md`)
- `python-expert`
- `python-clean-code`
- `python-design-modularity`
- `python-fastapi-development`
- `api-testing-patterns`
- `python-pytest-ops`
- `software-testing-tdd-architecture`
- `python-observability`
- `sade-surdurulebilir-mimari`
- `yazilim-prensipleri`

Duruma bağlı skill'ler:
- `data-analyst` — SQL metadata filtreleri ve query doğruluğu incelenecekse.
- `data-exploration` — retrieval recall/context kalitesi analiz edilecekse.
- `data-storytelling` — RAG yanıt formatı ve kullanıcıya anlaşılır açıklama tasarlanacaksa.
- `write-api-reference` — chat/search endpoint referans dokümanı yazılacaksa.

Özel notlar:
- Embedding provider olarak Jina CLIP v2 korunur.
- LLM API key yoksa mock provider/streaming testleri kullanılır.
- UI yoktur; sadece API ve streaming response contract'ı yapılır.
- Görseller local diskten bağlanır; Supabase'te BLOB beklenmez.

---

### `.planning/phases/03b-puqai-kriz/PLAN.md`

Faz: PUQ AI Bildirim & Yedek Parça Krizi Otomasyonu

Kapsam özeti:
- PUQ AI webhook client.
- Telegram/e-posta/SMS payload template'leri.
- Retry + webhook log.
- Offline fallback.
- Kriz skoru.
- Mock PO oluşturma.
- Alternatif tedarikçi tarama.
- Notification ve spare-parts FastAPI endpoint'leri.

Zorunlu skill'ler:
- `graphify`
- `karpathy-guidelines` (`andrej-karpathy-skills-main/skills/karpathy-guidelines/SKILL.md`)
- `python-expert`
- `python-clean-code`
- `python-design-modularity`
- `python-fastapi-development`
- `api-testing-patterns`
- `python-pytest-ops`
- `software-testing-tdd-architecture`
- `python-observability`
- `data-analyst`
- `sade-surdurulebilir-mimari`
- `yazilim-prensipleri`

Duruma bağlı skill'ler:
- `data-storytelling` — bildirim metinleri ve demo kriz anlatısı yazılacaksa.
- `data-visualization` — kriz skoru veya tedarikçi karşılaştırma raporları grafiklenecekse.
- `github-actions-cicd-architecture` — webhook mock/live testleri CI'a eklenecekse.
- `corporate-git-ci-standards` — webhook/kriz/PO değişiklikleri atomic commitlere ayrılacaksa.

Özel notlar:
- PUQ AI webhook URL yoksa live gönderim iddiası yapılmaz.
- Retry senaryoları 200/500/offline mock server ile test edilir.
- Mock PO gerçek satın alma yapmaz; `ready_for_review` ve manuel onay simülasyonu sınırdır.
- Alternatif tedarikçi önerisi mock supplier verisine dayanır.

---

### `.planning/phases/04-fastapi-entegrasyon/PLAN.md`

Faz: FastAPI Lifespan & Entegrasyon

Kapsam özeti:
- Tüm router'ların tek FastAPI app altında birleşmesi.
- Lifespan startup/shutdown.
- Config validation.
- Health check.
- Global exception handler.
- Structured logging.
- CORS.
- Integration tests.
- OpenAPI/Swagger dokümantasyonu.
- Dependency güncelleme.

Zorunlu skill'ler:
- `graphify`
- `karpathy-guidelines` (`andrej-karpathy-skills-main/skills/karpathy-guidelines/SKILL.md`)
- `python-fastapi-development`
- `python-design-modularity`
- `python-clean-code`
- `python-expert`
- `api-testing-patterns`
- `python-pytest-ops`
- `software-testing-tdd-architecture`
- `python-observability`
- `write-api-reference`
- `sade-surdurulebilir-mimari`
- `yazilim-prensipleri`

Duruma bağlı skill'ler:
- `docker-patterns` — NovaVision/local service health entegrasyonu Docker Compose veya container lifecycle'a bağlanacaksa.
- `github-actions-cicd-architecture` — full mock integration suite CI'a eklenecekse.
- `corporate-git-ci-standards` — final entegrasyon PR/commit düzeni yapılacaksa.
- `data-storytelling` — final entegrasyon raporu/demo akışı yazılacaksa.

Özel notlar:
- Mock/live servis durumları health response'ta açıkça ayrılır.
- Environment eksikse sessiz yanlış live mode'a geçilmez.
- OpenAPI dokümantasyonu tamamlanmadan production-ready sayılmaz.
- E2E mock zinciri veri → embedding → inference → bildirim ve kriz → PO akışını doğrulamalıdır.

---

## Skill kapsam dışı notları

Aşağıdaki skill'ler mevcut backend planlarında ana iş için varsayılan değildir; sadece açık UI/UX veya dokümantasyon görevi gelirse kullanılmalı:

- `frontend-design`
- `ux-designer`
- `popular-web-designs`
- `write-api-reference` dışındaki Next.js odaklı API dokümantasyon alt görevleri

Aşağıdaki skill'ler ise proje dışı veya çok özel amaçlıdır; ilgili doğrudan istek yoksa kullanılmamalıdır:

- `document-public-apis`
- `andrej-karpathy-skills-main/skills/karpathy-guidelines` dışındaki bundle dokümanları

## Bakım kuralı

Yeni bir `PLAN.md` eklendiğinde bu dosyaya yeni bölüm ekle. Yeni bir proje skill'i eklendiğinde mevcut faz eşleşmelerinde gerçekten kullanılıp kullanılmayacağını gözden geçir.
