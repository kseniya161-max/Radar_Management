from fastapi import APIRouter, status, Depends

from app.core.security import create_access_token
from app.database.db import SessionDep
from app.schemas.user import SUserCreate, SUserResponse, SUserLogin, SToken
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
    authentication = await authenticate_user(session, form_data.username, form_data.password)
    token = create_access_token(authentication.id)
    return {"access_token": token, "token_type": "bearer"}
