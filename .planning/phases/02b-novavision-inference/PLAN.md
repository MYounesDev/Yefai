---
phase: 2B
name: "NovaVision Local Inference Pipeline"
goal: "NovaVision CLI ile local Docker container kur, model deploy et, preprocessing + inference pipeline, FastAPI endpoint'leri."
depends_on: "Phase 1, Phase 2A (model .pt — sadece son entegrasyon)"
estimated_effort: "1.5 hafta"
manual_gate: "G2 — Docker Desktop kurulu, novavision CLI kurulu, NovaVision token alınmış"
parallel: true
parallel_with: "Phase 2A"
assignee: "Kişi B"
---

# Plan: Phase 2B — NovaVision Local Inference Pipeline

## Goal
NovaVision CLI ile local Docker container kur, Phase 2A'dan gelen .pt modelini app olarak deploy et, localhost REST API üzerinden inference yap, FastAPI endpoint'lerini yaz. Model gelene kadar mock ile çalış. **Tamamen local — bulut yok, API key yok.**

## Prerequisites (Manual Gate G2)
- [ ] Docker Desktop kurulu (`docker --version`)
- [ ] `pipx install novavision-cli` yapıldı (`novavision --help` çalışıyor)
- [ ] NovaVision token alındı (novavision.ai'den)
- [ ] `novavision install local <TOKEN>` çalıştı, Docker Compose hazır
- [ ] `NOVAVISION_TOKEN` ve `NOVAVISION_INFERENCE_URL` `.env` dosyasında

---

## Tasks

### Wave 1: NovaVision CLI Wrapper

#### Task 1.1: NovaVision CLI wrapper
- **Files:** `server/ai/novavision/cli.py`
- **Description:**
  - `novavision` CLI'ı Python `subprocess` ile yönet:
    ```python
    def novavision_start_server():
        subprocess.run(["novavision", "start", "server"], check=True)
    
    def novavision_deploy_app(model_path: Path, app_name: str):
        subprocess.run(["novavision", "deploy", "--model", str(model_path), ...])
    
    def novavision_start_app(app_id: str):
        subprocess.run(["novavision", "start", "app", "--id", app_id], check=True)
    ```
  - Docker Compose durumunu kontrol et (`docker ps`)
  - Container health check: `GET http://localhost:<PORT>/health`
  - Log toplama: `docker logs <container_id>`
- **UAT:** `novavision start server` çalışıyor, container health check 200

#### Task 1.2: NovaVision config & health
- **Files:** `server/ai/novavision/config.py`
- **Description:**
  - `.env` yapılandırması:
    - `NOVAVISION_TOKEN`: kullanıcı token'ı
    - `NOVAVISION_HOST`: varsayılan `alfa.suite.novavision.ai` (CI/CD host — model deploy için)
    - `NOVAVISION_INFERENCE_URL`: varsayılan `http://localhost:8501` (Docker container)
    - `NOVAVISION_MOCK`: mock mode (model yokken `true`)
  - Container durum sorgulama
  - Otomatik restart stratejisi
- **UAT:** Config doğru yükleniyor, container URL'ine ping atılabiliyor

### Wave 2: Model Deploy Pipeline

#### Task 2.1: Model deploy servisi
- **Files:** `server/ai/novavision/deploy.py`, `server/services/novavision_service.py`
- **Description:**
  - Phase 2A'dan gelen `.pt` dosyasını NovaVision app olarak deploy et
  - Deploy akışı:
    1. `novavision start server` (Docker altyapısı)
    2. Model dosyasını NovaVision formatına hazırla (preprocessing config ile)
    3. `novavision start app --id <APP_ID>` (modeli container'da başlat)
    4. Container health check → inference URL'i hazır
  - Model versiyonlama: her deploy yeni app ID
  - Supabase `novavision_models` tablosunda takip
- **UAT:** Deploy sonrası `curl localhost:8501/health` 200

#### Task 2.2: Model yönetimi
- **Files:** `server/ai/novavision/models.py`
- **Description:**
  - Deploy edilmiş modelleri listele (`docker ps --filter "name=novavision"`)
  - Model durumu: running, stopped, error
  - Eski model versiyonlarını durdur (`novavision stop app --id <ID>`)
  - Supabase `novavision_models` tablosunda durum takibi
- **UAT:** Çoklu model deploy edilebiliyor, durumları doğru

### Wave 3: Local Inference Pipeline

#### Task 3.1: Preprocessing pipeline
- **Files:** `server/ai/novavision/preprocessing.py`
- **Description:**
  - Görüntü ön işleme: resize (256x256), normalize, center crop
  - Batch preprocessing: çoklu görüntü için
  - Preprocessing config: NovaVision container'ın beklediği formata uygun
  - Görüntü format validasyonu (JPEG/PNG, minimum çözünürlük)
  - Local diskten görüntü yükleme (`data/MATWI/{file_path}`)
- **UAT:** Preprocessed görüntü container'a gönderilebilir formatta

#### Task 3.2: Inference client (local REST API)
- **Files:** `server/ai/novavision/inference.py`, `server/ai/novavision/schemas.py`
- **Description:**
  - `httpx.AsyncClient` ile localhost container'a istek:
    ```python
    async def infer(image_path: str) -> InferenceResult:
        image_bytes = await load_and_preprocess(image_path)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.novavision_inference_url}/infer",
                json={"image": image_bytes, "model_id": current_model_id},
                timeout=30.0
            )
            return InferenceResult(**resp.json())
    ```
  - Request/Response Pydantic modelleri:
    - `InferenceRequest`: image (base64), model_id
    - `InferenceResponse`: job_id, status
    - `InferenceResult`: anomaly_score, anomaly_map, wear_type, processing_time
  - Sonuçları Supabase `anomalies` tablosuna yaz
  - **Mock mode:** Container yokken (model deploy edilmemişken) fake sonuç
- **UAT:** Container çalışırken inference 2-5 saniyede sonuç dönüyor

#### Task 3.3: Container lifecycle yönetimi
- **Files:** `server/ai/novavision/lifecycle.py`
- **Description:**
  - FastAPI lifespan içinde container yönetimi (Phase 4'te bağlanacak)
  - Startup: `novavision start server` + `novavision start app --id <ID>`
  - Shutdown: `novavision stop app --id <ID>` + `novavision stop server`
  - Crash recovery: container düşerse otomatik restart
  - Sağlık kontrolü: 30 saniyede bir health check
- **UAT:** FastAPI restart'ta container otomatik başlıyor

### Wave 4: FastAPI Endpoint'leri

#### Task 4.1: NovaVision router
- **Files:** `server/routers/novavision.py`
- **Description:**
  - `POST /api/novavision/deploy` — model deploy et (body: model_path, app_name)
  - `GET /api/novavision/models` — deploy edilmiş modelleri listele
  - `GET /api/novavision/models/{app_id}` — model durumu
  - `DELETE /api/novavision/models/{app_id}` — modeli durdur ve kaldır
  - `POST /api/novavision/inference` — inference başlat (body: image_id veya image_base64)
  - `GET /api/novavision/inference/{job_id}` — sonuç sorgula
  - `GET /api/novavision/health` — container + model durumu
- **UAT:** Swagger UI'da tüm endpoint'ler görünür

#### Task 4.2: Gerçek entegrasyon testi (model gelince)
- **Files:** `tests/test_novavision_live.py`
- **Description:**
  - Phase 2A'dan model .pt dosyası al
  - `novavision deploy` ile container'a yükle
  - Test görüntüsü ile inference çalıştır
  - Sonucu doğrula (anomaly score > 0)
  - Performans ölç: deploy süresi, inference latency
  - **Bu task 2 saatte biter, 2A bitene kadar mock ile çalışılır**
- **UAT:** Gerçek model ile inference sonucu Phase 2A sonucuyla tutarlı

---

## Verification

- [ ] Docker + NovaVision CLI kurulu, container çalışıyor
- [ ] Mock mode'da tüm endpoint'ler test edilebiliyor
- [ ] Model deploy pipeline'ı hatasız
- [ ] Localhost REST API inference 2-5 saniyede sonuç dönüyor
- [ ] Container lifecycle: start/stop/restart sorunsuz
- [ ] Phase 2A modeli gerçek container'da inference veriyor (model gelince)

## must_haves

1. **Docker container çalışır durumda** — NovaVision inference için
2. **Mock mode tam çalışıyor** — Model gelmeden tüm endpoint'ler test edilebilir
3. **Local REST API client hatasız** — Preprocessing + inference + sonuç alma
4. **Container lifecycle robust** — Crash'te otomatik restart
5. **Gerçek model entegrasyonu 2 saat** — Model .pt gelince hızlı entegrasyon

## Deliverables
- `server/ai/novavision/cli.py` + `config.py`
- `server/ai/novavision/deploy.py` + `models.py`
- `server/ai/novavision/inference.py` + `schemas.py` + `preprocessing.py`
- `server/ai/novavision/lifecycle.py`
- `server/routers/novavision.py`
- `server/services/novavision_service.py`
- `tests/test_novavision_live.py`

## Implementation status — 2026-05-16

- Mock-mode NovaVision wrapper, deploy/model/inference service layer and FastAPI router implemented.
- `/api/novavision/deploy`, `/api/novavision/models`, `/api/novavision/models/{app_id}`, `DELETE /api/novavision/models/{app_id}`, `/api/novavision/inference`, `/api/novavision/inference/{job_id}`, and `/api/novavision/health` are available in OpenAPI.
- Live NovaVision behavior remains behind Manual Gate G2; no live deploy/inference success is claimed without token, local install, container and Phase 2A model artifact.
- Verification report: `reports/novavision_phase02b.md`.
