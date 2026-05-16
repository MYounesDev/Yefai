from fastapi import APIRouter, Depends, HTTPException, status

from auth.dependencies import get_org_context, require_permission
from auth.models import OrgContext
from auth.permissions import Permission
from ai.novavision.schemas import (
    DeployedModel,
    DeployRequest,
    HealthResponse,
    InferenceRequest,
    InferenceResponse,
    InferenceResult,
)
from services.novavision_service import NovaVisionService, get_novavision_service

router = APIRouter(prefix="/api/novavision", tags=["novavision"])


@router.post("/deploy", response_model=DeployedModel)
async def deploy_model(
    request: DeployRequest,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.MANAGE_ORG_SETTINGS)),
    service: NovaVisionService = Depends(get_novavision_service),
) -> DeployedModel:
    try:
        return await service.deploy(request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/models", response_model=list[DeployedModel])
def list_models(
    org: OrgContext = Depends(get_org_context),
    service: NovaVisionService = Depends(get_novavision_service),
) -> list[DeployedModel]:
    return service.models()


@router.get("/models/{app_id}", response_model=DeployedModel)
def get_model(
    app_id: str,
    org: OrgContext = Depends(get_org_context),
    service: NovaVisionService = Depends(get_novavision_service)
) -> DeployedModel:
    model = service.model(app_id)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NovaVision model not found"
        )
    return model


@router.delete("/models/{app_id}", response_model=DeployedModel)
def delete_model(
    app_id: str,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.MANAGE_ORG_SETTINGS)),
    service: NovaVisionService = Depends(get_novavision_service)
) -> DeployedModel:
    return service.delete_model(app_id)


@router.post("/inference", response_model=InferenceResponse)
async def start_inference(
    request: InferenceRequest,
    org: OrgContext = Depends(get_org_context),
    _: None = Depends(require_permission(Permission.VIEW_ANOMALIES)),
    service: NovaVisionService = Depends(get_novavision_service),
) -> InferenceResponse:
    try:
        return await service.run_inference(request)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/inference/{job_id}", response_model=InferenceResult)
def get_inference_result(
    job_id: str,
    org: OrgContext = Depends(get_org_context),
    service: NovaVisionService = Depends(get_novavision_service)
) -> InferenceResult:
    result = service.inference_result(job_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inference job not found")
    return result


@router.get("/health", response_model=HealthResponse)
async def health(
    org: OrgContext = Depends(get_org_context),
    service: NovaVisionService = Depends(get_novavision_service)
) -> HealthResponse:
    return await service.health()
