from pprint import pprint

from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv


class Settings(BaseSettings):
    COOKIE_NAME: str
    COOKIE_SECRET: str
    OPENAI_API_KEY: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    MCP_SERVER_URL: str

    class Config:
        _env_file = None
        extra = "allow"

load_dotenv(find_dotenv())

settings = Settings(_env_file=find_dotenv())

pprint(settings.model_dump())

