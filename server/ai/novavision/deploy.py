from pathlib import Path
from uuid import uuid4

from ai.novavision.cli import (
    container_health,
    novavision_deploy_app,
    novavision_start_app,
    novavision_start_server,
)
from ai.novavision.config import NovaVisionSettings, get_novavision_settings
from ai.novavision.schemas import DeployedModel, DeployRequest, ModelStatus


async def deploy_model(
    request: DeployRequest, settings: NovaVisionSettings | None = None
) -> DeployedModel:
    settings = settings or get_novavision_settings()
    model_path = Path(request.model_path)

    if settings.novavision_mock:
        return DeployedModel(
            app_id=f"mock-{uuid4()}",
            app_name=request.app_name,
            model_path=request.model_path,
            status=ModelStatus.MOCK,
            inference_url=str(settings.novavision_inference_url),
            mock=True,
        )

    if not model_path.exists():
        raise FileNotFoundError(f"Model artifact not found: {model_path}")
    novavision_start_server(settings=settings)
    novavision_deploy_app(model_path, request.app_name, settings=settings)
    app_id = f"{request.app_name}-{uuid4()}"
    novavision_start_app(app_id, settings=settings)
    status = ModelStatus.RUNNING if await container_health(settings) else ModelStatus.ERROR
    return DeployedModel(
        app_id=app_id,
        app_name=request.app_name,
        model_path=str(model_path),
        status=status,
        inference_url=str(settings.novavision_inference_url),
    )
