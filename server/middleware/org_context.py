"""Middleware to extract and validate the X-Organization-Id header.

This middleware runs on every request and stores the org_id in request.state
so downstream code can access it without header parsing. It does NOT enforce
authentication — that is handled by the auth dependencies.
"""

import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class OrgContextMiddleware(BaseHTTPMiddleware):
    """Extract X-Organization-Id header and store in request.state.org_id."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        org_id = request.headers.get("X-Organization-Id")
        request.state.org_id = org_id  # None if header not present

        response = await call_next(request)
        return response
