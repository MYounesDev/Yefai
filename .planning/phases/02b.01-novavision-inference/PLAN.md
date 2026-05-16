---
phase: 02b.01
name: "NovaVision CLI Reality Fix — App-ID Based Local Inference"
goal: "Mevcut NovaVision CLI'ın gerçek komut setine göre Phase 2B entegrasyonunu düzelt: deploy komutunu kaldır, app_id tabanlı start/inference akışına geç."
depends_on: "Phase 2B mock contract, Manual Gate G2"
estimated_effort: "0.5-1 gün"
manual_gate: "G2 — NovaVision token, novavision install local <TOKEN>, platformda hazırlanmış APP_ID"
parallel: false
assignee: "Kişi B"
---

# Plan: Phase 02b.01 — NovaVision CLI Reality Fix

## Problem

Kurulu NovaVision CLI gerçek komut seti şudur:

```bash
novavision install
novavision start
novavision stop
```

`novavision deploy` yoktur.

Doğrulanan help çıktısı:

```text
usage: novavision [-h] {install,start,stop} ...
```

Bu nedenle mevcut Phase 2B planında ve kodunda geçen aşağıdaki varsayım yanlıştır:

```bash
novavision deploy --model <model_path> --name <app_name>
```

Canlı modda şu dosyadaki wrapper çalışmaz:

```text
server/ai/novavision/cli.py
```

Çünkü live branch olmayan bir CLI komutunu çağırır.

## Corrected Architecture

NovaVision tarafında `.pt` modeli lokal CLI ile deploy etmiyoruz. Model/app NovaVision platform tarafında hazırlanmış olmalı; local CLI sadece server ve app başlatır.

Doğru akış:

```text
NovaVision platformunda model/app hazırlanır
        ↓
APP_ID alınır
        ↓
local makinede:
novavision install local <TOKEN>
novavision start server
novavision start app --id <APP_ID>
        ↓
Yefai FastAPI image inference isteğini NovaVision local inference URL'e yollar
```

Runtime path:

```text
Client
  -> Yefai FastAPI /api/novavision/inference
    -> http://localhost:8501/infer
      -> NovaVision local app container
```

## Scope

Bu phase sadece mevcut Phase 2B entegrasyonunu gerçek CLI davranışına uydurur.

Kapsamda:

- `novavision deploy` varsayımını koddan ve planlardan kaldırmak
- `model_path` tabanlı deploy yerine `app_id` tabanlı app başlatma kontratı kurmak
- `/api/novavision/deploy` endpoint'ini yeniden anlamlandırmak veya yeni endpoint'e taşımak
- live testleri `.pt model path` yerine `NOVAVISION_APP_ID` ile çalışacak şekilde güncellemek
- mock testlerin mevcut yeşil durumunu korumak

Kapsam dışı:

- NovaVision platformunda model/app oluşturma otomasyonu
- `.pt` dosyasını NovaVision platformuna upload etme
- Cloud inference ekleme
- Phase 2A Anomalib lokal inference hattını değiştirme

## Manual Gate G2.1

Canlı doğrulama için insan tarafından hazırlanmalı:

- [ ] NovaVision token mevcut
- [ ] `novavision install local <TOKEN>` çalıştırıldı
- [ ] NovaVision platformunda model/app oluşturuldu
- [ ] `APP_ID` alındı
- [ ] `.env` içinde aşağıdakiler var:

```env
NOVAVISION_MOCK=false
NOVAVISION_TOKEN=...
NOVAVISION_INFERENCE_URL=http://localhost:8501
NOVAVISION_DEFAULT_APP_ID=<APP_ID>
```

Opsiyonel live test env:

```env
NOVAVISION_TEST_APP_ID=<APP_ID>
NOVAVISION_TEST_IMAGE_PATH=/absolute/path/to/test-image.jpg
```

## Tasks

### Task 1 — CLI wrapper'ı gerçek komut setine indir

Files:

```text
server/ai/novavision/cli.py
```

Changes:

- `novavision_deploy_app(model_path, app_name, ...)` fonksiyonunu kaldır veya deprecated yap.
- Yeni fonksiyon ekle:

```python
def novavision_start_app(app_id: str, settings: NovaVisionSettings | None = None) -> CommandResult:
    return _run(["novavision", "start", "app", "--id", app_id], timeout=120.0)
```

- `novavision_start_server` aynen kalır:

```bash
novavision start server
```

- `novavision_stop_app` aynen app_id ile çalışır:

```bash
novavision stop app --id <APP_ID>
```

Acceptance:

- Kod hiçbir yerde `novavision deploy` çağırmaz.
- Mock mode davranışı bozulmaz.

### Task 2 — Schema kontratını app_id tabanlı yap

Files:

```text
server/ai/novavision/schemas.py
```

Current wrong-ish contract:

```python
class DeployRequest(BaseModel):
    model_path: str
    app_name: str = "yefai-novavision"
```

Replace with app start/register contract:

```python
class AppStartRequest(BaseModel):
    app_id: str
    app_name: str = "yefai-novavision"
```

veya geriye dönük uyumluluk gerekiyorsa:

```python
class DeployRequest(BaseModel):
    app_id: str
    app_name: str = "yefai-novavision"
    model_path: str | None = None  # deprecated, live mode uses app_id only
```

Acceptance:

- API request body artık canlı mod için `app_id` ister.
- `model_path` varsa sadece mock/legacy bilgi olarak kalır, CLI'a gönderilmez.

### Task 3 — Deploy service'i app start/register service'e çevir

Files:

```text
server/ai/novavision/deploy.py
server/services/novavision_service.py
```

New live behavior:

```text
1. novavision start server
2. novavision start app --id <APP_ID>
3. GET <NOVAVISION_INFERENCE_URL>/health
4. DeployedModel döndür: app_id, app_name, status, inference_url
```

Remove:

```bash
novavision deploy --model ...
```

Do not require:

```text
model_path exists
```

Acceptance:

- `/api/novavision/deploy` veya yeni `/api/novavision/apps/start` endpoint'i live modda app_id ile çalışır.
- Model path yok diye 404 dönmez.
- Health check fail olursa status `error` döner.

### Task 4 — Router endpoint adlarını netleştir

Files:

```text
server/routers/novavision.py
```

Preferred API:

```text
POST /api/novavision/apps/start
GET  /api/novavision/models
GET  /api/novavision/models/{app_id}
DELETE /api/novavision/models/{app_id}
POST /api/novavision/inference
GET  /api/novavision/inference/{job_id}
GET  /api/novavision/health
```

Compatibility option:

- `/api/novavision/deploy` kalabilir ama açıklaması değiştirilir:
  - Eski anlam: local `.pt` deploy
  - Yeni anlam: platformda var olan `app_id`'yi localde başlat/register et

Acceptance:

- Swagger/OpenAPI açıklamaları deploy kelimesiyle yanlış `.pt upload` beklentisi yaratmaz.
- Request örneği `model_path` değil `app_id` gösterir.

### Task 5 — Inference path'i app_id/default_app_id ile doğrula

Files:

```text
server/ai/novavision/inference.py
```

Behavior:

- `request.model_id` varsa onu kullan.
- Yoksa `settings.novavision_default_app_id` kullan.
- Payload mevcut gibi kalabilir:

```json
{
  "image": "<base64>",
  "mime_type": "image/jpeg",
  "model_id": "<APP_ID>"
}
```

Acceptance:

- Inference sırasında `.pt` dosyası gönderilmez.
- Sadece image/base64 ve model_id/app_id gönderilir.

### Task 6 — Tests güncelle

Files:

```text
tests/phase02b/test_novavision_mock.py
tests/test_novavision_live.py
```

Mock tests:

- deploy/start endpoint body `app_id` ile test edilmeli.
- model_path zorunlu olmamalı.

Live tests:

Remove dependency:

```text
NOVAVISION_TEST_MODEL_PATH
```

Use:

```text
NOVAVISION_TEST_APP_ID
NOVAVISION_TEST_IMAGE_PATH
NOVAVISION_MOCK=false
```

Live test command:

```bash
cd /home/furkan/Projects/Yefai/server
NOVAVISION_MOCK=false \
NOVAVISION_TEST_APP_ID=<APP_ID> \
NOVAVISION_TEST_IMAGE_PATH=/absolute/path/to/image.jpg \
uv run pytest ../tests/test_novavision_live.py -q -m live
```

Acceptance:

- Mock suite passes.
- Live tests skip with clear message if `NOVAVISION_TEST_APP_ID` missing.

### Task 7 — Planning/docs düzelt

Files:

```text
.planning/ROADMAP.md
.planning/STATE.md
.planning/phases/02b-novavision-inference/PLAN.md
.planning/phases/02b-novavision-inference/SUMMARY.md
.planning/phases/02b-novavision-inference/02b-VALIDATION.md
reports/novavision_phase02b.md
```

Changes:

- `novavision deploy` referanslarını kaldır.
- `.pt model local CLI deploy` iddiasını kaldır.
- G2 durumunu güncelle:
  - Docker + CLI var
  - CLI deploy desteklemiyor
  - canlı yol platform APP_ID + local start app
- Phase 2A `.pt artifact` bağımlılığını Phase 2B live local CLI için kaldır veya yeniden ifade et:
  - `.pt` NovaVision platformunda app/model oluşturmak için gerekebilir
  - Yefai local runtime için gereken şey `APP_ID`

Acceptance:

- `.planning` içinde `novavision deploy` geçmez veya sadece “geçersiz/eski varsayım” olarak açıklanır.
- Live validation `NOVAVISION_TEST_APP_ID` ister.

## Verification

Run from `server/`:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest ../tests/phase02b ../tests/test_novavision_live.py -q
```

Expected mock result:

```text
phase02b tests pass
live tests skip if NOVAVISION_TEST_APP_ID / NOVAVISION_TEST_IMAGE_PATH missing
```

Manual live verification after G2.1:

```bash
novavision start server
novavision start app --id <APP_ID>
curl http://localhost:8501/health
```

Then:

```bash
cd /home/furkan/Projects/Yefai/server
NOVAVISION_MOCK=false \
NOVAVISION_TEST_APP_ID=<APP_ID> \
NOVAVISION_TEST_IMAGE_PATH=/absolute/path/to/image.jpg \
uv run pytest ../tests/test_novavision_live.py -q -m live
```

## Done Criteria

- [ ] Kodda live path hiçbir yerde `novavision deploy` çağırmıyor.
- [ ] Start/register endpoint app_id ile çalışıyor.
- [ ] Mock tests green.
- [ ] Live tests doğru env eksikse skip ediyor.
- [ ] `.planning` ve raporlar gerçek CLI davranışıyla tutarlı.
- [ ] Manual live smoke için komutlar net.

## Notes

Bu phase, Phase 2B'nin önceki mock contract'ını çöpe atmaz. Sadece canlı NovaVision entegrasyon varsayımını düzeltir:

Eski yanlış varsayım:

```text
local .pt -> novavision deploy -> local app
```

Yeni doğru varsayım:

```text
NovaVision platform app/model -> APP_ID -> novavision start app --id APP_ID -> local inference
```
