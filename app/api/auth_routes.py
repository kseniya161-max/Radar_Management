from fastapi import APIRouter, status, Depends, HTTPException
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.database.db import SessionDep
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    SUserCreate,
    SUserResponse,
    SUserLogin,
    SToken,
    SAccessToken,
    SRefreshRequest,
)
from app.services.user_service import register_user, authenticate_user
from fastapi.security import OAuth2PasswordRequestForm

router_auth = APIRouter(prefix="/auth", tags=["Registration"])


@router_auth.post(
    "/register", response_model=SUserResponse, status_code=status.HTTP_201_CREATED
)
async def register(session: SessionDep, data: SUserCreate):
    new_user = await register_user(session, data.email, data.password)
    await session.commit()
    return new_user


@router_auth.post("/login", response_model=SToken, status_code=status.HTTP_200_OK)
async def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    authentication = await authenticate_user(
        session, form_data.username, form_data.password
    )

    token = create_access_token(authentication.id)
    refresh_token = create_refresh_token(authentication.id)

    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router_auth.post("/refresh", response_model=SAccessToken)
async def token_refresh(data: SRefreshRequest, session: SessionDep):
    payload = verify_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Неверный тип токена")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    new_access = create_access_token(user_id)
    return {"access_token": new_access, "token_type": "bearer"}
