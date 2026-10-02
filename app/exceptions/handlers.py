from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.ai import AiAPIError
from app.exceptions.checko import CheckoAPIError
from app.exceptions.company_exc import CompanyNotFoundError
from app.exceptions.user import UserAlreadyExistsError


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


async def ai_exception_handler(
    request: Request,
    exc: AiAPIError,
):
    return JSONResponse(
        status_code=503,
        content={
            "detail": str(exc),
        },
    )


async def company_exception_handler(
    request: Request,
    exc: CompanyNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )
