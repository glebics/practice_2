from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings


# Базовый класс для всех моделей
BaseModel = declarative_base()


# Создание движка и сессии
engine = create_engine(settings.database_url, pool_pre_ping=True)
Session = sessionmaker(bind=engine)


# Функция для создания всех таблиц
def create_all_tables() -> None:
    BaseModel.metadata.create_all(engine)
