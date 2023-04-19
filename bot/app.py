from flask import Flask, request, jsonify, send_file
from database.dbapi import DatabaseConnector
import pandas as pd
import tempfile
from database.models import Borrow, Book
import openpyxl
import xlsxwriter

app = Flask(__name__)

@app.route('/download/<int:book_id>')
def download_stats(book_id):
    # Получаем данные из базы данных
    db = DatabaseConnector()
    session = db.Session()
    query = session.query(Borrow).filter_by(book_id=book_id)
    df = pd.read_sql(query.statement, query.session.bind)
    # Удаляем столбец user_id
    # df.drop('user_id', axis=1, inplace=True)

    # Создаем временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        # Записываем данные в файл
        writer = pd.ExcelWriter(tmp.name, engine='xlsxwriter', date_format="dd mm yyyy")
        df.to_excel(writer, index=False, sheet_name=f"Sheet {book_id}")
        writer.close()
    # Отправляем файл пользователю
    return send_file(tmp.name, as_attachment=True, download_name=f'stats_book_{book_id}.xlsx')
