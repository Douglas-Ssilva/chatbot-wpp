import os
from dotenv import load_dotenv

# carrega env (só dev, se quiser)
if os.getenv("ENV") != "prod":
    load_dotenv(".env.dev")

class Settings:
    HOST_API: str = os.getenv("HOST_API")
    API_KEY: str = os.getenv("API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    FERNET_KEY = os.getenv('FERNET_KEY')

settings = Settings()