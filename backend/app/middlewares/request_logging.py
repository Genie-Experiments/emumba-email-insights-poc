from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from config.LoggingConfig import logger
import time


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Incoming request: {request.method} {request.url}")
        logger.info(f"Headers: {request.headers}")
        response = await call_next(request)
        return response
