from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """Проверка занятости email"""
        user = await self.session.execute(select(User).where(User.email == email))
        return user.scalar_one_or_none()

    async def create_user(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self.session.add(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """Проверка по id существует ли пользователь"""
        user = await self.session.execute(select(User).where(User.id == user_id))
        return user.scalar_one_or_none()
