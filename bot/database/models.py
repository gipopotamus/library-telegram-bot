from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, func, PrimaryKeyConstraint, DateTime
from sqlalchemy.orm import declarative_base
Base = declarative_base()


class Book(Base):
    __tablename__ = 'books'
    book_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    published = Column(Integer, nullable=False)
    date_added = Column(Integer, nullable=False)
    date_deleted = Column(Integer, nullable=True)


class Borrow(Base):
    __tablename__ = 'borrows'
    borrow_id = Column(Integer, nullable = False, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=True)
    user_id = Column(Integer, nullable=False)