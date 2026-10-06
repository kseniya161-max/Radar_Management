from fastapi import APIRouter,status

from app.database.db import SessionDep
from app.schemas.user import SUserCreate, SUserResponse
from app.services.user_service import register_user

router_auth = APIRouter(prefix="/auth", tags=["Registration"])

@router_auth.post('/register',response_model=SUserResponse,status_code=status.HTTP_201_CREATED)
async def register(session:SessionDep, data: SUserCreate):
    new_user = await register_user(session, data.email, data.password)
    await session.commit()
    return new_user



