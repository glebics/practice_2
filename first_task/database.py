from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from config import settings


# Соглашение по именованию индексов, ограничений и других элементов БД
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


# Метаданные с настройками именования и схемой
metadata = MetaData(naming_convention=naming_convention, schema="your_schema")


# Базовый класс для всех моделей с метаданными
BaseModel = declarative_base(metadata=metadata)


# Создание движка и сессии
engine = create_engine(settings.database_url, pool_pre_ping=True)
Session = sessionmaker(bind=engine)


# Функция для создания всех таблиц
def create_all_tables() -> None:
    BaseModel.metadata.create_all(engine)
