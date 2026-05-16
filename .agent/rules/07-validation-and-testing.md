# Validation & Testing Rules

## Kesinlikle yapılacaklar
- Faz kapanmadan önce ilgili `*-VALIDATION.md` dosyasındaki verification map'i kontrol et.
- `tests/conftest.py` gibi ortak fixture altyapısını erken kur.
- Gerçek servis gerektiren testleri marker ile ayır; CI/smoke için mock testleri çalıştır.
- Feedback latency hedeflerini koru:
  - Phase 2B mock: < 90s
  - Phase 3A mock: < 90s
  - Phase 2A/Phase 4 mock-smoke: < 120s
- Mock server/respx/httpx mock ile webhook 200/500/retry senaryolarını test et.
- NovaVision mock mode'da container/model yokken endpointlerin test edilebilir olduğunu doğrula.
- RAG provider abstraction'ı mock streaming ile test et.
- E2E mock zinciri kur: veri → embedding → inference → bildirim ve kriz → PO.
- Full suite ve manual gate kontrolleri yeşil olmadan fazı tamamlandı sayma.
- Her kabul kriteri için rapor, artifact veya test çıktısı üret.

## Kesinlikle yapılmayacaklar
- Live token/service gerektiren testi varsayılan CI testine bağlama.
- Dış servis yokken live başarı iddiası üretme.
- Sadece happy path test edip retry, offline, eksik credential, path bulunamadı, empty type gibi hata durumlarını atlama.
- Veri leakage kontrolü olmayan model metriğini başarı kabul etme.
- Accuracy'yi sınıf dengesizliği raporu olmadan tek başarı metriği sayma.
- Faz planındaki manual-only verification maddelerini otomasyonla yapılmış gibi işaretleme.

## Faz bazlı kritik doğrulamalar
- Phase 1: dataset parse, set-bazlı split, Supabase schema, mock spare-parts dosyaları ve kalite raporları.
- Phase 2A: PatchCore train, model export, local inference, Jina CLIP embedding ve search.
- Phase 2B: NovaVision wrapper, config, mock mode, local REST client, container health.
- Phase 2.5: wear calibration, trend/projection, `hours_to_critical` entegrasyon alanları.
- Phase 3A: LLM abstraction, RAG context, SSE streaming, session ve hybrid search.
- Phase 3B: PUQ webhook payload, retry/log, crisis score, auto PO, alternative suppliers.
- Phase 4: lifespan, router birleşimi, health, error handling, logging, CORS, OpenAPI, E2E mock.
