from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

connect_args = {}

# Для PostgreSQL через psycopg2 включаем sslmode
# Railway public proxy: обычно нужен require
if settings.DATABASE_URL.startswith("postgresql"):
    connect_args["sslmode"] = settings.DB_SSLMODE

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()