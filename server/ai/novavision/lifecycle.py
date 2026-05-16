import asyncio
import contextlib
import logging

from ai.novavision.cli import (
    container_health,
    novavision_start_app,
    novavision_start_server,
    novavision_stop_app,
    novavision_stop_server,
)
from ai.novavision.config import NovaVisionSettings, get_novavision_settings

logger = logging.getLogger(__name__)


class NovaVisionLifecycle:
    def __init__(self, settings: NovaVisionSettings | None = None) -> None:
        self.settings = settings or get_novavision_settings()
        self._monitor_task: asyncio.Task[None] | None = None

    async def startup(self) -> None:
        if self.settings.novavision_mock:
            logger.info("NovaVision lifecycle started in mock mode")
            return
        novavision_start_server(self.settings)
        novavision_start_app(self.settings.novavision_default_app_id, self.settings)
        self._monitor_task = asyncio.create_task(self._monitor())

    async def shutdown(self) -> None:
        if self._monitor_task:
            self._monitor_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._monitor_task
        if not self.settings.novavision_mock:
            novavision_stop_app(self.settings.novavision_default_app_id, self.settings)
            novavision_stop_server(self.settings)

    async def _monitor(self) -> None:
        while True:
            await asyncio.sleep(30)
            if not await container_health(self.settings):
                logger.warning("NovaVision container unhealthy; attempting restart")
                novavision_start_server(self.settings)
                novavision_start_app(self.settings.novavision_default_app_id, self.settings)
