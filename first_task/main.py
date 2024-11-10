from .database import create_all_tables, Session
from .models import Book, Author, Genre
from sqlalchemy.exc import SQLAlchemyError


def test_crud_operations():
    # Создаем сессию
    session = Session()
    try:
        # Добавление нового автора и жанра
        new_author = Author(name_author="Лев Толстой")
        new_genre = Genre(name_genre="Роман")
        session.add(new_author)
        session.add(new_genre)
        session.commit()
        print("Автор и жанр успешно добавлены.")

        # Добавление новой книги
        new_book = Book(
            title="Война и мир",
            author_id=new_author.pk_author_id,
            genre_id=new_genre.pk_genre_id,
            price=750.0,
            amount=5
        )
        session.add(new_book)
        session.commit()
        print("Книга успешно добавлена.")

        # Обновление записи о книге
        book_to_update = session.query(Book).filter_by(
            title="Война и мир").first()
        if book_to_update:
            book_to_update.price = 800.0  # Обновляем цену книги
            session.commit()
            print("Цена книги успешно обновлена.")

        # Чтение записей из таблицы книг
        books = session.query(Book).all()
        print("Список книг:")
        for book in books:
            print(
                f"Название: {book.title}, Автор ID: {book.author_id}, Жанр ID: {book.genre_id}, Цена: {book.price}, Количество: {book.amount}")

        # Удаление записи о книге
        book_to_delete = session.query(Book).filter_by(
            title="Война и мир").first()
        if book_to_delete:
            session.delete(book_to_delete)
            session.commit()
            print("Книга успешно удалена.")

    except SQLAlchemyError as e:
        session.rollback()  # Откат изменений в случае ошибки
        print(f"Произошла ошибка при выполнении операций с базой данных: {e}")
    finally:
        session.close()  # Закрытие сессии


if __name__ == "__main__":
    # Создаем таблицы
    create_all_tables()
    print("Таблицы успешно созданы")

    # Выполняем операции для проверки
    test_crud_operations()
