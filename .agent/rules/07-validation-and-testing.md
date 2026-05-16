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
- **Her commit öncesi pre-commit hook çalıştır:** `ruff check`, `ruff format`, `mypy`, `pytest tests/phase* -q`
- **Paket yöneticisi olarak sadece `uv` kullan:** `uv add`, `uv run`, `uv sync`
- **Her faz sonunda tüm kalite gate'lerini çalıştır:**
  ```bash
  cd server
  uv run ruff check .        # lint + import sıralama
  uv run ruff format --check .  # format kontrolü
  uv run mypy .              # tip kontrolü
  uv run pytest ../tests/ -q # tüm testler
  ```

## Code Quality Gates (Commit öncesi sırasıyla)

| Gate | Komut | Yaptığı |
|------|-------|---------|
| 1. Lint | `uv run ruff check .` | PEP8, pyflakes, import sıralama, deprecated typing, bugbear |
| 2. Format | `uv run ruff format --check .` | Kod formatı (line-length 100, double quotes) |
| 3. Type check | `uv run mypy .` | Statik tip analizi |
| 4. Test | `uv run pytest ../tests/ -q` | Tüm unit/integration testler |

Bu sıralama `.github/workflows/ci.yml` ve `.pre-commit-config.yaml` ile otomatikleştirilmiştir.

## Kesinlikle yapılmayacaklar
- Live token/service gerektiren testi varsayılan CI testine bağlama.
- Dış servis yokken live başarı iddiası üretme.
- Sadece happy path test edip retry, offline, eksik credential, path bulunamadı, empty type gibi hata durumlarını atlama.
- Veri leakage kontrolü olmayan model metriğini başarı kabul etme.
- Accuracy'yi sınıf dengesizliği raporu olmadan tek başarı metriği sayma.
- Faz planındaki manual-only verification maddelerini otomasyonla yapılmış gibi işaretleme.
- `pip install` veya `pip` komutu kullanma; her şey için `uv` kullan.
- Lint/type hatası varken commit yapma.
- `# type: ignore` veya `# noqa` yorumunu gerekçesiz kullanma.

## Faz bazlı kritik doğrulamalar
- Phase 1: dataset parse, set-bazlı split, Supabase schema, mock spare-parts dosyaları ve kalite raporları.
- Phase 2A: PatchCore train, model export, local inference, Jina CLIP embedding ve search.
- Phase 2B: NovaVision wrapper, config, mock mode, local REST client, container health.
- Phase 2.5: wear calibration, trend/projection, `hours_to_critical` entegrasyon alanları.
- Phase 3A: LLM abstraction, RAG context, SSE streaming, session ve hybrid search.
- Phase 3B: PUQ webhook payload, retry/log, crisis score, auto PO, alternative suppliers.
- Phase 4: lifespan, router birleşimi, health, error handling, logging, CORS, OpenAPI, E2E mock.
