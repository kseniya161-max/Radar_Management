#Radar Management – B2B Lead Enrichment Microservice

Микросервис для автоматического поиска, сбора и обогащения данных о компаниях через API Checko.
Позволяет по коду ОКВЭД найти организации, получить их контакты, финансовые показатели и сохранить в PostgreSQL.
Предназначен для построения базы потенциальных клиентов («лидов») и последующего скоринга (оценки приоритета) с помощью AI.

# Основные возможности

* Поиск компаний по ОКВЭД (с фильтром только действующих).

* Сохранение базовых сведений (ИНН, название, статус, ОКВЭД, дата регистрации).

* Обогащение контактами: телефоны, email, веб-сайт, регион.

* Обогащение финансовыми данными: выручка за 2023–2025 годы.

* Единый эндпоинт /enrich для полного обогащения (контакты + финансы) одной компании.

* Готовые REST API для выборочного обновления и просмотра.

* HTTP-запросы (httpx) для высокой производительности.


# Стек технологий
* Python 3.11+

* FastAPI – веб‑фреймворк, автодокументация (Swagger/ReDoc)

* SQLAlchemy 2.x 

* PostgreSQL – основная база данных

* httpx – HTTP‑клиент

* Pydantic – валидация данных

* Alembic – миграции схемы БД

##  Установка и запуск

# Клонировать репозиторий

git clone https://github.com/yourusername/radarmanagement.git
cd radarmanagement

# Создать и активировать виртуальное окружение
python -m venv venv
source venv/bin/activate   
venv\Scripts\activate      

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения в .env

CHECKO_API_KEY=ваш_api_ключ_с_сайта_checko.ru
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/radarmanagement

# Создать базу данных PostgreSQL

CREATE DATABASE radarmanagement;

# Применить миграции 

alembic upgrade head

# Запустить сервер FastAPI
uvicorn app.main:app --reload

Swagger UI будет доступен по адресу http://127.0.0.1:8000/docs

# API Эндпоинты
Метод	Эндпоинт	Описание
GET	/ping	Проверка работоспособности
GET	/companies	Список всех компаний из БД
GET	/companies/{inn}	Детальная информация по ИНН
POST	/create/{okved_code}	Синхронизация компаний по ОКВЭД (только базовые данные)
POST	/companies/{inn}/contacts	Обновить контакты и регион для компании
POST	/companies/{inn}/finance	Обновить финансовые показатели
POST	/companies/{inn}/enrich	Полное обогащение (контакты + финансы)