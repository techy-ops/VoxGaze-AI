import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request execution duration, path, method, and HTTP status code.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Incoming Request: {request.method} {request.url.path} from {client_host}")

        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            logger.info(
                f"Response: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - Duration: {process_time:.2f}ms"
            )
            response.headers["X-Process-Time-MS"] = f"{process_time:.2f}"
            return response
        except Exception as exc:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Request Failed: {request.method} {request.url.path} - "
                f"Duration: {process_time:.2f}ms - Error: {str(exc)}"
            )
            raise exc
