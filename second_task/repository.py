from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, Dict, Any
from sqlalchemy import text


class Repository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def is_report_in_db(self, report_date: date) -> bool:
        """
        Проверяет, существует ли отчет для указанной даты в базе данных.
        """
        query = text("SELECT 1 FROM spimex_trading_results WHERE date = :date")
        result = self.db.execute(query, {"date": report_date}).fetchone()
        return result is not None

    def save_report_data(self, report_data: Dict[str, Any]) -> None:
        """
        Сохраняет данные отчета в базе данных.
        """
        self.db.execute(
            text(
                """
                INSERT INTO spimex_trading_results (exchange_product_id, exchange_product_name, oil_id, delivery_basis_id, 
                                                    delivery_basis_name, delivery_type_id, volume, total, count, date)
                VALUES (:exchange_product_id, :exchange_product_name, :oil_id, :delivery_basis_id, 
                        :delivery_basis_name, :delivery_type_id, :volume, :total, :count, :date)
                """
            ), report_data
        )
        self.db.commit()
