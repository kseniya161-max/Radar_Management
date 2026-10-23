import logging
import time
from fastapi import Request

logger = logging.getLogger("uvicorn")


async def log_companies_only(request: Request, call_next):

    if not request.url.path.startswith("/companies"):
        return await call_next(request)

    start = time.perf_counter()

    logger.info(f"запрос пришел {request.method} {request.url.path}")

    response = await call_next(request) # выполнить этот эндпоинт и дать мне его ответ

    duration = time.perf_counter() - start

    if duration > 5:
        logger.warning(
            f'Медленный запрос: {request.method} {request.url.path} '
            f'→ {response.status_code} ({duration:.2f}s)'
        )
    else:
        logger.info(f"запрос ушел клиенту {response.status_code} ({duration:.4f}s)")



    response.headers["X-Process-Time"] = f"{duration:.4f}s"

    return response
