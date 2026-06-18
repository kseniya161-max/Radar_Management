from sqlalchemy import String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


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
    region: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    profit_2023: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    profit_2024: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    profit_2025: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
