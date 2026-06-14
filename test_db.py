from app.core.config import settings
from app.database.session import SessionLocal
from app.services.company_service import get_companies
from app.clients.company_api_client import search_companies_by_okved, get_company_finances

db = SessionLocal()

# try:
#     companies = get_companies(db)
#
#     for company in companies:
#         print(
#             company.id,
#             company.inn,
#             company.name,
#             company.status,
#             company.okved,
#         )
# finally:
#     db.close()

# print(settings.CHECKO_API_KEY)

# def test():
#     inn = '4027148080'
#     result = get_companies_info(inn)
#     print(result.get("data", {}).get("НаимПолн"))
#
# if __name__ == "__main__":
#     test()

# result = search_companies_by_okved("01.4")
# print(result)

# from app.database.session import SessionLocal
# from app.clients.company_api_client import sync_companies
#
# session = SessionLocal()
#
# sync_companies("46.72", session)
#
# session.close()


# from app.clients.company_api_client import get_company_contacts
#
# data = get_company_contacts("3528015184")
#
# print(data)


# from app.clients.company_api_client import (
#     get_company_contacts,
#     parse_contacts,
# )
#
# data = get_company_contacts("3528015184")
#
# contacts = parse_contacts(data)
#
# print(contacts)
#
#
# from app.database.session import SessionLocal
# from app.clients.company_api_client import update_company_contacts
#
# session = SessionLocal()
#
# update_company_contacts(
#     session,
#     "3528015184"
# )
#
# session.close()

# from app.database.session import SessionLocal
# from app.clients.company_api_client import update_company_contacts
#
# session = SessionLocal()
#
# update_company_contacts(
#     session,
#     "3528015184"
# )
#
# session.close()
#
# data = get_company_finances("3528015184")
#
# print(data)


data = get_company_finances("3528015184")

print(data)