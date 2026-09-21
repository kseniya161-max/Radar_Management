from sqlalchemy import String, BigInteger, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base
from enum import Enum


class Progress(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    REJECTED = "rejected"
    TRANSFERRED = "transferred"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    inn: Mapped[str] = mapped_column(String(12), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))
    okved: Mapped[str] = mapped_column(String(255))
    revenue_2025: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    revenue_2024: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    revenue_2023: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    tenders_count: Mapped[int] = mapped_column(default=0)
    courts_count: Mapped[int] = mapped_column(default=0)
    phone: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    email: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    website: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    registration_date: Mapped[str] = mapped_column(
        String(255), nullable=True, default=None
    )
    region: Mapped[str] = mapped_column(
        String(255), nullable=True, default=None, index=True
    )
    profit_2023: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    profit_2024: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    profit_2025: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    revenue_growth_3: Mapped[float | None] = mapped_column(nullable=True)
    profit_growth_3: Mapped[float | None] = mapped_column(nullable=True)
    ai_priority: Mapped[int | None] = mapped_column(nullable=True, index=True)
    ai_risk: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    progress: Mapped[Progress] = mapped_column(
        SAEnum(
            Progress,
            name="company_progress",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=Progress.ACTIVE,
        server_default="active",
        index=True,
    )
