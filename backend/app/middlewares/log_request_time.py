# middleware.py
import time
from fastapi import Request
from config.LoggingConfig import (
    logger,
)


async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"Request: {request.method} {request.url} - Completed in {duration:.4f} seconds"
    )
    return response
