from models import SpimexTradingResult
from database import Base, engine
import re
import os
import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from database import get_db, SessionLocal
from sqlalchemy.orm import Session
import pandas as pd
from sqlalchemy import text

# Настройка логирования
logging.basicConfig(level=logging.INFO)

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

BASE_URL = "https://spimex.com/markets/oil_products/trades/results/"

# Создаем таблицы в базе данных, если они еще не существуют
Base.metadata.create_all(bind=engine)


def calculate_months_limit() -> int:
    """
    Вычисляет количество месяцев между начальной и текущей датами.

    Returns:
        int: Количество месяцев между начальной и текущей датами.
    """
    start_date = datetime(2023, 1, 1)
    current_date = datetime.now()
    months_diff = (current_date.year - start_date.year) * \
        12 + current_date.month - start_date.month
    return months_diff


def fetch_report_links() -> list[str]:
    """
    Получает ссылки на отчетные файлы с сайта SPIMEX.

    Returns:
        list[str]: Список ссылок на отчетные файлы.
    """
    session = requests.Session()
    page_number = 1
    months_limit = calculate_months_limit()
    collected_links = []

    while len(collected_links) < months_limit:
        url = f"{BASE_URL}?page={page_number}"
        response = session.get(url)

        if response.status_code != 200:
            logging.info(
                f"Ошибка загрузки страницы {page_number}. Код ответа: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.select("a.accordeon-inner__item-title.link.xls")

        for link in links:
            if "Бюллетень по итогам торгов в Секции «Нефтепродукты»" in link.text:
                href = link.get("href")
                full_link = f"https://spimex.com{href}"
                collected_links.append(full_link)
                print(f"Ссылка на файл: {full_link}")

                if len(collected_links) >= months_limit:
                    break

        page_number += 1

    return collected_links[:10]


def extract_trade_date(file_path: str) -> datetime.date | None:
    """
    Извлекает дату торгов из указанного файла Excel.

    Args:
        file_path (str): Путь к файлу Excel.

    Returns:
        datetime.date | None: Дата торгов или None, если дата не найдена.
    """
    try:
        df = pd.read_excel(file_path, header=None)
        for row in df.itertuples(index=False):
            for cell in row:
                if isinstance(cell, str) and "Дата торгов:" in cell:
                    date_match = re.search(r"\d{2}\.\d{2}\.\d{4}", cell)
                    if date_match:
                        trade_date = datetime.strptime(
                            date_match.group(), "%d.%m.%Y")
                        logging.info(
                            f"Дата торгов успешно извлечена: {trade_date.date()}")
                        return trade_date.date()
        logging.error(f"Дата не найдена в файле {file_path}")
        return None
    except Exception as e:
        logging.error(f"Ошибка извлечения даты из файла {file_path}: {e}")
        return None


def report_exists(date: datetime.date) -> bool:
    """
    Проверяет, существует ли отчет для указанной даты в локальной файловой системе.

    Args:
        date (datetime.date): Дата отчета.

    Returns:
        bool: True, если отчет существует, иначе False.
    """
    file_path = os.path.join(REPORTS_DIR, f"{date}.xls")
    return os.path.exists(file_path)


def is_report_in_db(report_date: datetime.date, db: Session) -> bool:
    """
    Проверяет, существует ли отчет для указанной даты в базе данных.

    Args:
        report_date (datetime.date): Дата отчета.
        db (Session): Сессия базы данных.

    Returns:
        bool: True, если отчет существует в базе данных, иначе False.
    """
    query = text("SELECT 1 FROM spimex_trading_results WHERE date = :date")
    result = db.execute(query, {"date": report_date}).fetchone()
    return result is not None


def download_report(url: str, index: int) -> str | None:
    """
    Скачивает отчет по указанной ссылке и сохраняет его в локальной системе.

    Args:
        url (str): Ссылка на отчет.
        index (int): Индекс файла для временного сохранения.

    Returns:
        str | None: Путь к файлу отчета или None, если дата не была извлечена.
    """
    response = requests.get(url)
    if response.status_code == 200:
        temp_file_path = os.path.join(REPORTS_DIR, f"temp_report_{index}.xls")
        with open(temp_file_path, "wb") as file:
            file.write(response.content)

        report_date = extract_trade_date(temp_file_path)

        if report_date:
            if report_exists(report_date):
                logging.info(
                    f"Отчет за {report_date} уже существует. Пропуск скачивания.")
                os.remove(temp_file_path)
                return None

            final_file_path = os.path.join(REPORTS_DIR, f"{report_date}.xls")
            os.rename(temp_file_path, final_file_path)
            logging.info(f"Файл сохранен: {final_file_path}")
            return final_file_path
        else:
            os.remove(temp_file_path)
            logging.warning(
                f"Файл {temp_file_path} удален из-за отсутствия даты.")
            return None
    else:
        logging.error(
            f"Ошибка скачивания файла по ссылке {url}. Код ответа: {response.status_code}")
        return None


def save_report_to_db(file_path: str, db: Session) -> None:
    """
    Сохраняет данные из отчета в базе данных.

    Args:
        file_path (str): Путь к файлу отчета.
        db (Session): Сессия базы данных.
    """
    try:
        logging.info(
            f"Начало обработки файла '{file_path}' для записи в базу данных.")
        df = pd.read_excel(file_path, skiprows=6)
        df.columns = df.columns.to_series().ffill()
        df = df.fillna('')

        # Переименование столбцов для базы данных
        column_mapping = {
            'Код\nИнструмента': 'exchange_product_id',
            'Наименование\nИнструмента': 'exchange_product_name',
            'Базис\nпоставки': 'delivery_basis_id',
            'Объем\nДоговоров\nв единицах\nизмерения': 'volume',
            'Обьем\nДоговоров,\nруб.': 'total',
            'Цена в Заявках (за единицу\nизмерения)': 'delivery_type_id',
            'Количество\nДоговоров,\nшт.': 'count',
        }
        df.rename(columns=column_mapping, inplace=True)

        required_columns = list(column_mapping.values())
        missing_columns = [
            col for col in required_columns if col not in df.columns]
        if missing_columns:
            logging.warning(
                f"В файле '{file_path}' отсутствуют столбцы: {missing_columns}")
            return

        df = df[required_columns]
        df.replace({'-': None, '': None}, inplace=True)
        df = df[~df['exchange_product_id'].str.contains('Итого', na=False)]
        df.dropna(subset=['exchange_product_id',
                  'exchange_product_name', 'delivery_basis_id'], inplace=True)

        for _, row in df.iterrows():
            report_data = {
                "exchange_product_id": row['exchange_product_id'],
                "exchange_product_name": row['exchange_product_name'],
                "oil_id": row['exchange_product_id'][:4] if isinstance(row['exchange_product_id'], str) else None,
                "delivery_basis_id": row['delivery_basis_id'],
                "delivery_basis_name": "",
                "delivery_type_id": try_convert_to_float(row['delivery_type_id']),
                "volume": try_convert_to_float(row['volume']),
                "total": try_convert_to_float(row['total']),
                "count": try_convert_to_int(row['count']),
                "date": datetime.strptime(file_path.split("/")[-1].replace(".xls", ""), "%Y-%m-%d")
            }
            db.execute(
                text(
                    """
                    INSERT INTO spimex_trading_results (exchange_product_id, exchange_product_name, oil_id, delivery_basis_id, 
                                                        delivery_basis_name, delivery_type_id, volume, total, count, date)
                    VALUES (:exchange_product_id, :exchange_product_name, :oil_id, :delivery_basis_id, 
                            :delivery_basis_name, :delivery_type_id, :volume, :total, :count, :date)
                    """
                ), report_data
            )
        db.commit()
        logging.info(
            f"Данные из файла '{file_path}' успешно сохранены в базу данных.")

    except Exception as e:
        logging.error(
            f"Ошибка при сохранении данных из файла '{file_path}' в базу данных: {e}")
        db.rollback()


def try_convert_to_float(value: any) -> float | None:
    """
    Пытается преобразовать значение в float.

    Args:
        value (any): Значение для преобразования.

    Returns:
        float | None: Преобразованное значение или None, если преобразование невозможно.
    """
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None


def try_convert_to_int(value: any) -> int | None:
    """
    Пытается преобразовать значение в int.

    Args:
        value (any): Значение для преобразования.

    Returns:
        int | None: Преобразованное значение или None, если преобразование невозможно.
    """
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def main() -> None:
    """
    Основная функция программы, которая загружает отчеты, обрабатывает их и сохраняет в базу данных.
    """
    logging.info("Начало работы программы.")
    report_links = fetch_report_links()

    db = SessionLocal()
    try:
        for i, url in enumerate(report_links, start=1):
            logging.info(f"Скачивание отчета {i} из {len(report_links)}")
            file_path = download_report(url, i)

            if file_path:
                report_date = extract_trade_date(file_path)

                if report_date and not is_report_in_db(report_date, db):
                    logging.info(
                        f"Начало обработки и записи в базу данных для файла '{file_path}'")
                    save_report_to_db(file_path, db)
                else:
                    logging.info(
                        f"Отчет за {report_date} уже существует в базе данных. Пропуск записи.")

        # Проверка и запись всех файлов в папке 'reports'
        for filename in os.listdir(REPORTS_DIR):
            file_path = os.path.join(REPORTS_DIR, filename)
            report_date = extract_trade_date(file_path)

            if report_date and not is_report_in_db(report_date, db):
                logging.info(
                    f"Начало обработки и записи в базу данных для файла '{file_path}'")
                save_report_to_db(file_path, db)
            else:
                logging.info(
                    f"Отчет за {report_date} уже существует в базе данных. Пропуск записи.")

    finally:
        db.close()
        logging.info("Завершение работы программы.")


if __name__ == "__main__":
    main()
