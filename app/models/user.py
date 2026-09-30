from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        default=True, server_default="true", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=func.now(), nullable=False
    )
