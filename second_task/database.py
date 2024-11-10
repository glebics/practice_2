import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings  # Импортируем объект settings


# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Получаем URL базы данных из settings
try:
    DATABASE_URL = settings.database_url  # Используем database_url из settings
    logging.info("URL базы данных успешно получен из настроек.")
except Exception as e:
    logging.error(f"Ошибка при получении URL базы данных: {e}")
    raise


# Создание движка базы данных
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    logging.info("Движок базы данных успешно создан.")
except Exception as e:
    logging.error(f"Ошибка при создании движка базы данных: {e}")
    raise


# Создание сессии
try:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logging.info("SessionLocal успешно создан.")
except Exception as e:
    logging.error(f"Ошибка при создании SessionLocal: {e}")
    raise


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
Base = declarative_base(metadata=metadata)


# Функция для получения сессии
def get_db():
    logging.info("Создание сессии базы данных.")
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logging.error(f"Ошибка во время работы с сессией базы данных: {e}")
        raise
    finally:
        db.close()
        logging.info("Сессия базы данных закрыта.")
