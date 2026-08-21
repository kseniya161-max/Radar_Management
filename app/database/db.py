from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import SessionLocal



async def get_db():
    async with SessionLocal() as db:
        yield db


SessionDep = Annotated[AsyncSession, Depends(get_db)]
