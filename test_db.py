from sqlalchemy import select

from app.database.session import SessionLocal
from app.services.company_service import update_company_finances
from app.models.company import Company

session = SessionLocal()

inn = "2346010454"

try:

    company = session.scalar(
        select(Company).where(Company.inn == inn)
    )

    if not company:
        print("Такой компании нет в БД:", inn)
        exit()

    print("Компания найдена:", company.name)


    update_company_finances(session, inn)
    session.commit()


    session.expire_all()

    company = session.scalar(
        select(Company).where(Company.inn == inn)
    )


    print("РЕЗУЛЬТАТ:")
    print("revenue_2023:", company.revenue_2023)
    print("revenue_2024:", company.revenue_2024)
    print("revenue_2025:", company.revenue_2025)

finally:
    session.close()