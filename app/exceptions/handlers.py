from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.checko import CheckoAPIError


async def checko_exception_handler(
    request: Request,
    exc: CheckoAPIError,
):
    return JSONResponse(
        status_code=503,
        content={
            "detail": str(exc),
        },
    )