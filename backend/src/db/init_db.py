from src.db.session import engine
from src.db.base import Base
from src import models  # важно: чтобы метадата увидела все таблицы

def init_db() -> None:
    Base.metadata.create_all(bind=engine)