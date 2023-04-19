if __name__ == "__main__":
    from database import *
    from app import app
    from telegram import bot
else:
    from .database import *
    from .app import app
    from .telegram import bot

from threading import Thread

class ServerThread(Thread):
    def run(self) -> None:
        app.run('0.0.0.0', port=8080)

class TgThread(Thread):
    def run(self) -> None:
        bot.infinity_polling()



if __name__ == "__main__":
    serv_thread = ServerThread()
    serv_thread.start()
    tg_thread = TgThread()
    tg_thread.start()
