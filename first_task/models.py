from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import BaseModel


# Таблица жанров
class Genre(BaseModel):
    __tablename__ = 'genre'
    __table_args__ = {
        "comment": "Таблица, содержащая информацию о жанрах книг"}

    pk_genre_id = Column(Integer, primary_key=True,
                         comment="Уникальный идентификатор жанра")
    name_genre = Column(String, nullable=False, comment="Название жанра")

    # Связь с книгами
    books = relationship("Book", back_populates="genre")


# Таблица авторов
class Author(BaseModel):
    __tablename__ = 'author'
    __table_args__ = {"comment": "Таблица, содержащая информацию об авторах"}

    pk_author_id = Column(Integer, primary_key=True,
                          comment="Уникальный идентификатор автора")
    name_author = Column(String, nullable=False, comment="Имя автора")

    # Связь с книгами
    books = relationship("Book", back_populates="author")


# Таблица городов
class City(BaseModel):
    __tablename__ = 'city'
    __table_args__ = {
        "comment": "Таблица, содержащая информацию о городах доставки"}

    pk_city_id = Column(Integer, primary_key=True,
                        comment="Уникальный идентификатор города")
    name_city = Column(String, nullable=False, comment="Название города")
    days_delivery = Column(Integer, nullable=False,
                           comment="Количество дней для доставки в город")

    # Связь с клиентами
    clients = relationship("Client", back_populates="city")


# Таблица клиентов
class Client(BaseModel):
    __tablename__ = 'client'
    __table_args__ = {"comment": "Таблица, содержащая информацию о клиентах"}

    pk_client_id = Column(Integer, primary_key=True,
                          comment="Уникальный идентификатор клиента")
    name_client = Column(String, nullable=False, comment="Имя клиента")
    city_id = Column(Integer, ForeignKey('city.pk_city_id'),
                     comment="Идентификатор города проживания клиента")
    email = Column(String, nullable=False, comment="Электронная почта клиента")

    # Связи с другими таблицами
    city = relationship("City", back_populates="clients")
    purchases = relationship("Purchase", back_populates="client")


# Таблица книг
class Book(BaseModel):
    __tablename__ = 'book'
    __table_args__ = {"comment": "Таблица, содержащая информацию о книгах"}

    pk_book_id = Column(Integer, primary_key=True,
                        comment="Уникальный идентификатор книги")
    title = Column(String, nullable=False, comment="Название книги")
    author_id = Column(Integer, ForeignKey(
        'author.pk_author_id'), comment="Идентификатор автора книги")
    genre_id = Column(Integer, ForeignKey('genre.pk_genre_id'),
                      comment="Идентификатор жанра книги")
    price = Column(Float, nullable=False, comment="Цена книги")
    amount = Column(Integer, nullable=False,
                    comment="Количество экземпляров книги в наличии")

    # Связи с другими таблицами
    author = relationship("Author", back_populates="books")
    genre = relationship("Genre", back_populates="books")
    buy_books = relationship("PurchaseBook", back_populates="book")


# Таблица покупок
class Purchase(BaseModel):
    __tablename__ = 'purchase'
    __table_args__ = {
        "comment": "Таблица, содержащая информацию о покупках клиентов"}

    pk_buy_id = Column(Integer, primary_key=True,
                       comment="Уникальный идентификатор покупки")
    buy_description = Column(String, comment="Описание покупки")
    client_id = Column(Integer, ForeignKey('client.pk_client_id'),
                       comment="Идентификатор клиента, совершившего покупку")

    # Связи с другими таблицами
    client = relationship("Client", back_populates="purchases")
    buy_books = relationship("PurchaseBook", back_populates="purchase")
    buy_steps = relationship("PurchaseStep", back_populates="purchase")


# Таблица этапов покупки
class Step(BaseModel):
    __tablename__ = 'step'
    __table_args__ = {
        "comment": "Таблица, содержащая информацию о различных этапах покупки"}

    pk_step_id = Column(Integer, primary_key=True,
                        comment="Уникальный идентификатор этапа")
    name_step = Column(String, nullable=False, comment="Название этапа")

    # Связь с таблицей buy_step
    buy_steps = relationship("PurchaseStep", back_populates="step")


# Таблица покупаемых книг
class PurchaseBook(BaseModel):
    __tablename__ = 'buy_book'
    __table_args__ = {
        "comment": "Таблица, содержащая информацию о книгах, приобретенных в рамках покупок"}

    pk_buy_book_id = Column(Integer, primary_key=True,
                            comment="Уникальный идентификатор записи о приобретенной книге")
    buy_id = Column(Integer, ForeignKey('purchase.pk_buy_id'),
                    comment="Идентификатор покупки")
    book_id = Column(Integer, ForeignKey('book.pk_book_id'),
                     comment="Идентификатор книги")
    amount = Column(Integer, nullable=False,
                    comment="Количество экземпляров книги, приобретенных в рамках покупки")

    # Связи с другими таблицами
    purchase = relationship("Purchase", back_populates="buy_books")
    book = relationship("Book", back_populates="buy_books")


# Таблица шагов покупки
class PurchaseStep(BaseModel):
    __tablename__ = 'buy_step'
    __table_args__ = {
        "comment": "Таблица, связывающая этапы покупки с конкретными покупками"}

    pk_buy_step_id = Column(Integer, primary_key=True,
                            comment="Уникальный идентификатор шага в процессе покупки")
    buy_id = Column(Integer, ForeignKey('purchase.pk_buy_id'),
                    comment="Идентификатор покупки")
    step_id = Column(Integer, ForeignKey('step.pk_step_id'),
                     comment="Идентификатор этапа покупки")
    date_step_beg = Column(DateTime, nullable=False,
                           comment="Дата начала этапа покупки")
    date_step_end = Column(DateTime, comment="Дата окончания этапа покупки")

    # Связи с другими таблицами
    purchase = relationship("Purchase", back_populates="buy_steps")
    step = relationship("Step", back_populates="buy_steps")
