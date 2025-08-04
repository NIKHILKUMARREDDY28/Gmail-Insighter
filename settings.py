from pprint import pprint

from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv


class Settings(BaseSettings):
    APP_NAME: str = "Gmail Summariser"
    COOKIE_NAME: str
    COOKIE_SECRET: str
    OPENAI_API_KEY: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    MCP_SERVER_URL: str
    FERNET_KEY: str
    REDIS_HOST: str = "redis://localhost:6379"

    class Config:
        _env_file = None
        extra = "allow"

load_dotenv(find_dotenv())

settings = Settings(_env_file=find_dotenv())

pprint(settings.model_dump())

