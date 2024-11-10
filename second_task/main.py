import logging
from database import SessionLocal
from repository import Repository
from service import SpimexService


def main() -> None:
    logging.info("Начало работы программы.")
    db = SessionLocal()
    try:
        repository = Repository(db)
        service = SpimexService(repository)

        months_limit = service.calculate_months_limit()
        report_links = service.fetch_report_links(months_limit)
        service.download_and_save_reports(report_links)

    finally:
        db.close()
        logging.info("Завершение работы программы.")


if __name__ == "__main__":
    main()
