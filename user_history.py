import sqlite3
from sys import exit, argv
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog


class UserHistory(QDialog):
    def __init__(self, user_name, user_type):
        super().__init__()
        uic.loadUi('user_history.ui', self)
        self.user_name = user_name
        self.owner_history.setText({'user': 'пользователя', 'developer': 'разработчика'}[user_type])
        self.owner_name.setText(self.user_name)
        self.set_history()

    def set_history(self):
        db = sqlite3.connect('databases\\user_history_db.sqlite')
        cursor = db.cursor()
        history = cursor.execute("SELECT user_history FROM users_history "
                                 "WHERE user_name like ?", [self.user_name]).fetchall()
        if not history[0][0]:
            history = 'Пусто'
        else:
            history = '\n'.join(history[0][0].split(';')[1:])
        self.history.setText(history)
        cursor.close()


if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(argv)
    w = UserHistory('Валера', 'developer')
    w.show()
    exit(app.exec())
