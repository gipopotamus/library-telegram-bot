from sqlalchemy import create_engine, select, DateTime
from sqlalchemy.orm import sessionmaker 
import datetime 
from sqlalchemy import(
    Column, Integer, String, Date, Text, ForeignKey, UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import relationship
from dataclasses import dataclass
from sqlalchemy import func
from database.models import Book, Borrow
import getpass


@dataclass
class DatabaseConnector:
    def __init__(self) -> None:
        USERNAME = getpass.getuser()
        connection_string = f"postgresql+psycopg2://{USERNAME}:@localhost:5432/{USERNAME}"
        engine = create_engine(connection_string)
        self.Session = sessionmaker(engine)
         

    def add(self, title_, author_, published_):
        try:
            session = self.Session()
            check = session.query(Book).filter(Book.title == title_, Book.author == author_, Book.published == published_).one_or_none()
            if check is not None:
                if check.date_deleted is None:
                    raise Exception
                else:
                    check.date_deleted = None
                    check.date_added = datetime.datetime.now().strftime('%Y-%m-%d')
                    session.commit()
                    return check.book_id
            else:
                today = datetime.datetime.now().strftime('%Y-%m-%d')
                book = Book(title=title_, author=author_, published=published_, date_added = today, date_deleted = None)
                session.add(book)
                session.commit()
                return book.book_id
        except: return False
        finally: session.close()

    def delete(self, book_id):
        try:
            session = self.Session()
            book = session.query(Book).filter(Book.book_id == book_id).first()
            if book is None: return False 

            borrow = session.query(Borrow).filter(Borrow.book_id == book_id, Borrow.date_end == None).first()
            if borrow is not None: return False

            today = datetime.datetime.now().strftime('%Y-%m-%d')
            book.date_deleted = today
            session.commit()
            return True
        except: return False
        finally: session.close()

    def list_books(self):
        session = self.Session()
        allbooks = []
        try:
            books = session.query(Book.title, Book.author, Book.published, Book.date_deleted).all()
            allbooks = [book for book in books]
            return allbooks
        except: return False
        finally: session.close()

    def get_book(self, title, author):
        try:
            session = self.Session()
            bookid = session.query(Book.book_id).where(func.lower(Book.title) == title.lower(), func.lower(Book.author) == author.lower()).first()
            return bookid[0]
        except: return False
        finally: session.close()

    def borrow(self, book_id, user_id):
        try:
            session = self.Session()
            # Проверка на то, что книга не удалена
            book = session.query(Book).where(Book.book_id == book_id).first()
            if book.date_deleted is not None:
                print('book is deleted')
                return False

            #Проверка на то, что книга не возвращена
            book_borrowed = session.query(Borrow.borrow_id).where(Borrow.book_id == book_id, Borrow.date_end == None).all()
            if len(book_borrowed) > 0:
                print('book is borrowed')
                return False

            #Проверка на то, что юзер не вернул книгу
            user = session.query(Borrow.borrow_id).where(Borrow.user_id == user_id, Borrow.date_end == None).all()
            if len(user) > 0:
                print('user didnt return book')
                return False
            
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            borrow = Borrow(book_id = book_id, date_start = today, user_id = user_id)
            session.add(borrow)
            session.commit()
            return borrow.borrow_id
        except Exception as e: print(e) 
        finally: session.close()

    def get_borrow(self, user_id):
        try:
            session = self.Session()
            borrow = session.query(Borrow.borrow_id).where(Borrow.user_id == user_id, Borrow.date_end == None).first()
            return borrow
        except: return False
        finally: session.close()

    def retrieve(self, user_id):
        try:        
            session = self.Session()
            check = session.query(Borrow.date_end).where(Borrow.user_id == user_id, Borrow.date_end == None).one_or_none()
            if check is None:
                return False
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            id = session.query(Borrow.book_id).where(Borrow.user_id == user_id, Borrow.date_end == None).first()
            print(id)
            if id is None:
                return False
            query = session.query(Borrow).where(Borrow.user_id == user_id, Borrow.date_end == None).one_or_none()
            query.date_end = today
            get_book_attributes = session.query(Book.title, Book.author, Book.published).where(Book.book_id == id[0]).first()
            session.commit()
            return get_book_attributes
        except Exception as e: print(e)
        finally: session.close()
