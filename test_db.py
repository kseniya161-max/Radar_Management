from sqlalchemy import select

from app.database.session import SessionLocal
from app.services.company_service import update_company_finances
from app.models.company import Company
#
# session = SessionLocal()
#
# inn = "6901069168"
#
# try:
#
#     company = session.scalar(
#         select(Company).where(Company.inn == inn)
#     )
#
#     if not company:
#         print("Такой компании нет в БД:", inn)
#         exit()
#
#     print("Компания найдена:", company.name)
#
#
#     update_company_finances(session, inn)
#     session.commit()
#
#
#     session.expire_all()
#
#     company = session.scalar(
#         select(Company).where(Company.inn == inn)
#     )
#
#
#     print("РЕЗУЛЬТАТ:")
#     print("revenue_2023:", company.revenue_2023)
#     print("revenue_2024:", company.revenue_2024)
#     print("revenue_2025:", company.revenue_2025)
#
# finally:
#     session.close()


from app.database.db import SessionLocal
from app.models.company import Company

session = SessionLocal()
companies = session.query(Company).limit(5).all()
for comp in companies:
    print(f"{comp.name} | рег. дата: {comp.registration_date}")
session.close()