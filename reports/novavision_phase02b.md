# Phase 2B NovaVision Local Inference — Implementation Report

## Scope

Bu rapor Phase 2B planındaki NovaVision local inference pipeline uygulamasının mevcut durumunu özetler.

## Implemented

- NovaVision CLI wrapper: `server/ai/novavision/cli.py`
- NovaVision settings/config: `server/ai/novavision/config.py`
- Deploy pipeline service: `server/ai/novavision/deploy.py`
- Model listing/status/stop helpers: `server/ai/novavision/models.py`
- Image/base64 preprocessing contract: `server/ai/novavision/preprocessing.py`
- Local REST inference client with mock fallback: `server/ai/novavision/inference.py`
- Container lifecycle helper: `server/ai/novavision/lifecycle.py`
- Pydantic request/response schemas: `server/ai/novavision/schemas.py`
- Service layer: `server/services/novavision_service.py`
- FastAPI router: `server/routers/novavision.py`
- Router registration and `/health` NovaVision mode summary: `server/main.py`
- Mock-mode API tests: `tests/phase02b/test_novavision_mock.py`
- Live/manual-gate test skeleton: `tests/test_novavision_live.py`
- Root pytest marker registration: `pytest.ini`

## Manual Gate G2 status

Checked locally:

- `docker --version`: available
- `novavision --help`: available

Not claimed as completed automatically:

- NovaVision token presence was not verified.
- `novavision install local <TOKEN>` was not run.
- Real Phase 2A `.pt` model artifact was not deployed.
- Live container inference was not claimed.

## Mock/live behavior

Default mode is mock (`NOVAVISION_MOCK=true`). In mock mode all `/api/novavision/*` endpoints are testable without NovaVision token, Docker container, or model artifact.

Live mode requires:

- `NOVAVISION_MOCK=false`
- `NOVAVISION_TOKEN`
- `NOVAVISION_INFERENCE_URL`
- `NOVAVISION_TEST_MODEL_PATH` for live tests
- `NOVAVISION_TEST_IMAGE_PATH` for live tests

## Verification run

From `server/`:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run --extra dev pytest ../tests/ -q
```

Results:

- Ruff check: passed
- Ruff format check: passed
- Mypy: passed
- Pytest: 51 passed, 2 skipped

The 2 skipped tests are live NovaVision tests that require G2 credentials/container/model.
