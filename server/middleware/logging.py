"""Request logging middleware."""

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("yefai.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing and org_id."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        org_id = request.headers.get("X-Organization-Id", "-")
        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration={duration:.3f}s "
            f"org={org_id}"
        )
        return response
