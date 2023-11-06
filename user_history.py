import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

"""
Класс, который открывает окно с историей загруженных видео пользователя
"""


class UserHistory(QDialog):
    def __init__(self, user_name, user_type):
        super().__init__()
        uic.loadUi('user_history.ui', self)
        self.user_name = user_name
        self.owner_history.setText({'user': 'пользователя', 'developer': 'разработчика'}[user_type])
        self.owner_name.setText(self.user_name)
        self.set_history()

    def set_history(self):
        db = sqlite3.connect('databases\\users_db.sqlite')
        cursor = db.cursor()
        history = cursor.execute("SELECT user_history FROM users_history "
                                 "WHERE user_name like ?", [self.user_name]).fetchall()
        if not history[0][0]:
            history = 'Пусто'
        else:
            history = '\n'.join(history[0][0].split(';')[1:])
        self.history.setText(history)
        cursor.close()
