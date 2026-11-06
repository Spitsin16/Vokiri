import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")


SECRET_KEY = os.getenv("SECRET_KEY")
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
GIGACHAT_VERSION= os.getenv("GIGACHAT_VERSION")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
AI_DAILY_GENERATION_LIMIT = int(os.getenv("AI_DAILY_GENERATION_LIMIT"))
OWNER_ID = int(os.getenv("OWNER_ID"))
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:4173,http://127.0.0.1:4173",
    ).split(",")
    if origin.strip()
]
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY is not configured")
if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not configured")
