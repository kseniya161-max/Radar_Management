import os
from dotenv import load_dotenv


load_dotenv()

class Settings:
    CHECKO_API_KEY: str = os.getenv("CHECKO_API_KEY", "")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()