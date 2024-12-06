import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL","postgresql://youruser:yourpassword@db:5432/yourdb")
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY",'AIzaSyB8iPyu4vC_MIiCxqwUqBwrLJwcrZ4HUCQ')
    GEMINI_MODEL =  'gemini-1.0-pro'
settings = Settings()
