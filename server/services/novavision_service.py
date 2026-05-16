import logging

from ai.novavision.cli import container_health
from ai.novavision.config import NovaVisionSettings, get_novavision_settings
from ai.novavision.deploy import deploy_model
from ai.novavision.inference import infer
from ai.novavision.models import get_model, list_models, stop_model
from ai.novavision.schemas import (
    DeployedModel,
    DeployRequest,
    HealthResponse,
    InferenceRequest,
    InferenceResponse,
    InferenceResult,
)

logger = logging.getLogger(__name__)

_INFERENCE_RESULTS: dict[str, InferenceResult] = {}


class NovaVisionService:
    def __init__(self, settings: NovaVisionSettings | None = None) -> None:
        self.settings = settings or get_novavision_settings()

    async def health(self) -> HealthResponse:
        healthy = await container_health(self.settings)
        mode = "mock" if self.settings.novavision_mock else "live"
        return HealthResponse(
            status="ok" if healthy else "unavailable",
            mode=mode,
            inference_url=str(self.settings.novavision_inference_url),
            container_running=healthy,
            active_app_id=self.settings.novavision_default_app_id,
            message="NovaVision mock mode active"
            if self.settings.novavision_mock
            else "NovaVision live mode",
        )

    async def deploy(self, request: DeployRequest) -> DeployedModel:
        return await deploy_model(request, self.settings)

    def models(self) -> list[DeployedModel]:
        return list_models(self.settings)

    def model(self, app_id: str) -> DeployedModel | None:
        return get_model(app_id, self.settings)

    def delete_model(self, app_id: str) -> DeployedModel:
        return stop_model(app_id, self.settings)

    async def run_inference(self, request: InferenceRequest) -> InferenceResponse:
        result = await infer(request, self.settings)
        _INFERENCE_RESULTS[result.job_id] = result
        logger.info(
            "NovaVision inference completed", extra={"job_id": result.job_id, "mock": result.mock}
        )
        return InferenceResponse(job_id=result.job_id, status=result.status, result=result)

    def inference_result(self, job_id: str) -> InferenceResult | None:
        return _INFERENCE_RESULTS.get(job_id)


def get_novavision_service() -> NovaVisionService:
    return NovaVisionService()
