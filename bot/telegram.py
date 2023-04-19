import telebot
import datetime
from telebot import types
from database.dbapi import DatabaseConnector
import app
bot = telebot.TeleBot("6034385955:AAFWKuRYQqe7ZMKv0HhwxOcuXkeVAzDVQyI")



@bot.message_handler(commands = ['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    _add = types.InlineKeyboardButton(text="/add")
    _delete = types.InlineKeyboardButton(text="/delete")
    _list = types.InlineKeyboardButton(text="/list")
    _find = types.InlineKeyboardButton(text="/find")
    _borrow = types.InlineKeyboardButton(text="/borrow")
    _retrieve = types.InlineKeyboardButton(text="/retrieve")
    _stats = types.InlineKeyboardButton(text="/stats")
    _break = types.InlineKeyboardButton(text="break")
    markup.add(_add, _delete, _list, _find, _borrow, _retrieve, _stats, _break)
    bot.send_message(message.from_user.id, "Привет!", reply_markup=markup)


@bot.message_handler(commands = ['add', 'delete', 'find', 'borrow', 'stats'])
def entry(message):
    command_name = message.text
    bot.send_message(message.from_user.id, "Введите название книги")
    bot.register_next_step_handler(message, get_book_title, command_name)

def get_book_title(message, command_name):
    if message.text == 'break':
        bot.send_message(message.from_user.id, "Операция прервана пользователем")
        return
    title = message.text
    bot.send_message(message.from_user.id, "Введите автора")
    bot.register_next_step_handler(message, get_author, title, command_name)

def get_author(message, title, command_name):
    if message.text == 'break':
        bot.send_message(message.from_user.id, "Операция прервана пользователем")
        return
    author = message.text
    bot.send_message(message.from_user.id, "Введите год издания")
    bot.register_next_step_handler(message, get_year, title, author, command_name)

def get_year(message, title, author, command_name):
    
    try:
        if message.text == 'break':
            bot.send_message(message.from_user.id, "Операция прервана пользователем")
            return
        year = int(message.text)
        if year < 0 or year > int(datetime.datetime.now().strftime("%Y")):
            raise ValueError
    except ValueError:
        bot.send_message(message.from_user.id, "Неверно введен год")
        return

    match command_name:
        case "/add":
            exemplar = DatabaseConnector()
            book_id = exemplar.add(title_=title, author_=author, published_=year)
            if book_id == False:
                bot.send_message(message.from_user.id, "Ошибка при добавлении книги")
                return
            else:
                bot.send_message(message.from_user.id, f"Добавлена книга с id {book_id}")
        case "/delete":
            exemplar = DatabaseConnector()
            book_idnum = exemplar.get_book(title, author)
            if book_idnum == False:
                bot.send_message(message.from_user.id, "Нет такой книги")
                return
            else:
                bot.send_message(message.from_user.id, f"Найдена книга: {title} {author} {year}. Удаляем?")
                bot.register_next_step_handler(message, resolve_delete, exemplar, book_idnum)
        case "/find":
            exemplar = DatabaseConnector()
            book_idnum = exemplar.get_book(title, author)
            if book_idnum == False:
                bot.send_message(message.from_user.id, f"Такой книги нет")
                return
            else:
                bot.send_message(message.from_user.id, f"Найдена книга: {title} {author} {year}")
                return
        case "/borrow":
            exemplar = DatabaseConnector()
            book_idnum = exemplar.get_book(title, author)
            if book_idnum == False:
                bot.send_message(message.from_user.id, "Нет такой книги")
                return
            else:
                bot.send_message(message.from_user.id, f"Найдена книга: {title} {author} {year}. Берем?")
                bot.register_next_step_handler(message, resolve_borrow, exemplar, book_idnum)
        case "/stats":
            exemplar = DatabaseConnector()
            book_idnum = exemplar.get_book(title, author)
            if book_idnum == False:
                bot.send_message(message.from_user.id, "Такой книги нет")
                return
            else:
                bot.send_message(message.from_user.id, f"Статистика доступна по ссылке http://127.0.0.1:8080/download/{book_idnum}")
                return


                
def resolve_delete(message, exemplar, book_idnum):
    if message.text == 'break':
        bot.send_message(message.from_user.id, "Операция прервана пользователем")
        return
    if message.text.lower() == 'да':
        exemplar.delete(book_idnum)
        bot.send_message(message.from_user.id, "Книга удалена")
        return
    elif message.text.lower() == 'нет':
        bot.send_message(message.from_user.id, "Ладно")
        return

def resolve_borrow(message, exemplar, book_idnum):
    if message.text == 'break':
        bot.send_message(message.from_user.id, "Операция прервана пользователем")
        return
    if message.text.lower() == 'да':
        state = exemplar.borrow(book_idnum, message.chat.id)
        if state == False:
            bot.send_message(message.from_user.id, "Невозможно арендовать книгу")
            return
        else:
            bot.send_message(message.from_user.id, "Арендовано")
            return
    elif message.text.lower() == 'нет':
        bot.send_message(message.from_user.id, "Ладно")
        return



@bot.message_handler(commands = ['list'])
def list(message):
    exemplar = DatabaseConnector()
    ans = exemplar.list_books()
    if len(ans) == 0:
        bot.send_message(message.from_user.id, "В библиотеке пока нет ни одной книги")
        return
    bot.send_message(message.from_user.id, "Список книг:")
    for elem in ans:
        if elem[3] is None:
            bot.send_message(message.from_user.id, f"{elem[0]}, {elem[1]}, {elem[2]}")
            return
        else:
            bot.send_message(message.from_user.id, f"{elem[0]}, {elem[1]}, {elem[2]} (удалена)")
            return



@bot.message_handler(commands = ['retrieve'])
def retrieve_book(message):
    exemplar = DatabaseConnector()
    retrieve_status = exemplar.retrieve(message.chat.id)
    if retrieve_status == False:
        bot.send_message(message.from_user.id, "Нечего возвращать")
        return
    else:
        bot.send_message(message.from_user.id, f"Вы вернули {retrieve_status[0]} {retrieve_status[1]} {retrieve_status[2]}")
        return

