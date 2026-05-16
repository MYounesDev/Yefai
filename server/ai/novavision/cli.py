import logging
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import httpx

from ai.novavision.config import NovaVisionSettings, get_novavision_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


def _run(command: Sequence[str], timeout: float = 60.0) -> CommandResult:
    logger.info("Running NovaVision command", extra={"command": list(command)})
    completed = subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if completed.returncode != 0:
        logger.warning(
            "NovaVision command failed",
            extra={"command": list(command), "stderr": completed.stderr},
        )
    return CommandResult(tuple(command), completed.returncode, completed.stdout, completed.stderr)


def novavision_start_server(settings: NovaVisionSettings | None = None) -> CommandResult:
    settings = settings or get_novavision_settings()
    if settings.novavision_mock:
        return CommandResult(("novavision", "start", "server"), 0, "mock mode", "")
    return _run(["novavision", "start", "server"], timeout=120.0)


def novavision_stop_server(settings: NovaVisionSettings | None = None) -> CommandResult:
    settings = settings or get_novavision_settings()
    if settings.novavision_mock:
        return CommandResult(("novavision", "stop", "server"), 0, "mock mode", "")
    return _run(["novavision", "stop", "server"], timeout=120.0)


def novavision_deploy_app(
    model_path: Path, app_name: str, settings: NovaVisionSettings | None = None
) -> CommandResult:
    settings = settings or get_novavision_settings()
    if settings.novavision_mock:
        return CommandResult(
            ("novavision", "deploy", "--model", str(model_path)), 0, "mock mode", ""
        )
    if not model_path.exists():
        raise FileNotFoundError(f"NovaVision model path does not exist: {model_path}")
    return _run(
        ["novavision", "deploy", "--model", str(model_path), "--name", app_name],
        timeout=300.0,
    )


def novavision_start_app(app_id: str, settings: NovaVisionSettings | None = None) -> CommandResult:
    settings = settings or get_novavision_settings()
    if settings.novavision_mock:
        return CommandResult(("novavision", "start", "app", "--id", app_id), 0, "mock mode", "")
    return _run(["novavision", "start", "app", "--id", app_id], timeout=120.0)


def novavision_stop_app(app_id: str, settings: NovaVisionSettings | None = None) -> CommandResult:
    settings = settings or get_novavision_settings()
    if settings.novavision_mock:
        return CommandResult(("novavision", "stop", "app", "--id", app_id), 0, "mock mode", "")
    return _run(["novavision", "stop", "app", "--id", app_id], timeout=120.0)


def docker_ps(container_name: str = "novavision") -> CommandResult:
    return _run(
        [
            "docker",
            "ps",
            "--filter",
            f"name={container_name}",
            "--format",
            "{{.ID}} {{.Names}} {{.Status}}",
        ],
        timeout=30.0,
    )


def docker_logs(container_id: str, tail: int = 100) -> CommandResult:
    return _run(["docker", "logs", "--tail", str(tail), container_id], timeout=30.0)


async def container_health(settings: NovaVisionSettings | None = None) -> bool:
    settings = settings or get_novavision_settings()
    if settings.novavision_mock:
        return True
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.novavision_inference_url}/health")
        return response.status_code == 200
    except httpx.HTTPError:
        logger.warning("NovaVision container health check failed", exc_info=True)
        return False
