import os
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("SECRET")


class Settings:
    SECRET_KEY: str = SECRET
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # in mins
    COOKIE_NAME = "access_token"


settings = Settings()
