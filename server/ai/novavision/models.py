from pathlib import Path

from ai.novavision.cli import docker_ps, novavision_stop_app
from ai.novavision.config import NovaVisionSettings, get_novavision_settings
from ai.novavision.schemas import DeployedModel, ModelStatus


def list_models(settings: NovaVisionSettings | None = None) -> list[DeployedModel]:
    settings = settings or get_novavision_settings()
    if settings.novavision_mock:
        return [
            DeployedModel(
                app_id=settings.novavision_default_app_id,
                app_name="Mock NovaVision Model",
                status=ModelStatus.MOCK,
                inference_url=str(settings.novavision_inference_url),
                mock=True,
            )
        ]

    result = docker_ps(settings.novavision_container_name)
    models: list[DeployedModel] = []
    for line in result.stdout.splitlines():
        parts = line.split(maxsplit=2)
        if len(parts) >= 2:
            models.append(
                DeployedModel(
                    app_id=parts[0],
                    app_name=parts[1],
                    status=ModelStatus.RUNNING,
                    inference_url=str(settings.novavision_inference_url),
                )
            )
    return models


def get_model(app_id: str, settings: NovaVisionSettings | None = None) -> DeployedModel | None:
    return next((model for model in list_models(settings) if model.app_id == app_id), None)


def stop_model(app_id: str, settings: NovaVisionSettings | None = None) -> DeployedModel:
    settings = settings or get_novavision_settings()
    if settings.novavision_mock:
        return DeployedModel(
            app_id=app_id,
            app_name="Mock NovaVision Model",
            status=ModelStatus.STOPPED,
            inference_url=str(settings.novavision_inference_url),
            mock=True,
        )
    novavision_stop_app(app_id, settings=settings)
    return DeployedModel(
        app_id=app_id,
        app_name=Path(app_id).name,
        status=ModelStatus.STOPPED,
        inference_url=str(settings.novavision_inference_url),
    )
