from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


async def register_user(db: AsyncSession, email:str, password: str) -> User:
    repo = UserRepository(db)
    check_email = await repo.get_by_email(email)
    if check_email:
        raise UserAlreadyExistsError(f"User with email {email} already exists")
    hashed = hash_password(password)
    user = await repo.create_user(email,hashed)
    return user

