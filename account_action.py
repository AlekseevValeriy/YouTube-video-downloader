import sqlite3
from sys import exit, argv
from datetime import datetime
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog


class AccountAction(QDialog):
    def __init__(self, window_title):
        super().__init__()
        uic.loadUi('account_action.ui', self)
        self.setWindowTitle(window_title)
        if window_title == 'Вход в аккаунт':
            self.button.clicked.connect(self.enter_in_db)
        elif window_title == 'Создание аккаунта':
            self.button.clicked.connect(self.create_acc_in_db)
        self.developer_status_create = False
        self.developer_status_user = False
        self.successful_login = False
        self.name = ''
        self.password = ''

    def keyPressEvent(self, event):
        if int(event.modifiers()) == (Qt.ControlModifier):
            if event.key() == Qt.Key_A:
                self.developer_status_create = True
                self.status_label.setText('Вы разработчик')


    def create_acc_in_db(self):
        db_users = sqlite3.connect('databases\\users_db.sqlite')
        db_history = sqlite3.connect('databases\\user_history_db.sqlite')
        cur_u = db_users.cursor()
        cur_h = db_history.cursor()
        coincidences = cur_u.execute("SELECT id FROM users "
                                     "WHERE user_name like ?", [self.name_line.text()]).fetchall()
        if not coincidences:
            user_status = 'user' if not self.developer_status_create else 'developer'
            user_account_information = [self.name_line.text(), self.password_line.text(), user_status,
                                        datetime.now().strftime('%d.%m.%Y')]
            cur_u.execute("INSERT INTO users(user_name, user_password, user_type, create_date) "
                          "VALUES(?, ?, ?, ?)", user_account_information).fetchall()
            db_users.commit()
            cur_u.close()

            user_history_information = [self.name_line.text(), '']
            cur_h.execute("INSERT INTO users_history(user_name, user_history) "
                          "VALUES(?, ?)", user_history_information).fetchall()
            db_history.commit()
            cur_h.close()
            self.successful_login = True
            self.name = self.name_line.text()
            self.status_label.setText('Вы создали аккаунт')
        else:
            self.clear()
            self.status_label.setText('Аккаунт с таким именем уже существует')

    def enter_in_db(self):
        db = sqlite3.connect('databases\\users_db.sqlite')
        cur = db.cursor()
        result = cur.execute("SELECT id, user_type FROM users "
                             "WHERE user_name like ? AND user_password like ?",
                             [self.name_line.text(), self.password_line.text()]).fetchall()
        if result and (result[0][1] != 'developer' or (result[0][1] == 'developer' and self.developer_status_create)):
            print(result)
            self.successful_login = True
            self.name = self.name_line.text()
            self.password = self.password_line.text()
            if result[0][1] == 'developer':
                self.developer_status_user = True
            self.status_label.setText('Вы вошли в аккаунт')
        elif not result:
            self.clear()
            self.status_label.setText('Такого аккаунта не существует')
        elif result[0][1] == 'developer' and not self.developer_status_create:
            self.clear()
            self.status_label.setText('Вы не являетесь разработчиком')

    def clear(self):
        self.developer_status_create = False
        self.developer_status_user = False
        self.successful_login = False
        self.name = ''
        self.password = ''

    @staticmethod
    def add_history(user_name, link: str):
        db = sqlite3.connect('databases\\user_history_db.sqlite')
        cur = db.cursor()
        old_history = cur.execute("SELECT user_history FROM users_history "
                                  "WHERE user_name like ?", [user_name]).fetchall()
        if old_history:
            result = cur.execute("UPDATE users_history "
                                 "SET user_history = ?"
                                 "WHERE user_name = ?",
                                 [';'.join([*old_history[0], link]), user_name]).fetchall()
        db.commit()
        cur.close()

    @staticmethod
    def clear_history(user_name):
        db = sqlite3.connect('databases\\user_history_db.sqlite')
        cur = db.cursor()
        result = cur.execute("UPDATE users_history "
                             "SET user_history = ''"
                             "WHERE user_name = ?", [user_name]).fetchall()
        db.commit()
        cur.close()

    @staticmethod
    def save_as_txt(user_name):
        db = sqlite3.connect('databases\\user_history_db.sqlite')
        cur = db.cursor()
        history = cur.execute("SELECT user_history FROM users_history "
                              "WHERE user_name like ?", [user_name]).fetchall()
        db.commit()
        cur.close()
        with open(f'user_history_{user_name}.txt', 'w+', encoding='utf-8') as history_file:
            history_file.write(f'user_history_{user_name}:\n' + history[0][0].replace(';', '\n'))
            print('ok')

if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(argv)
    w = AccountAction('Вход в аккаунт')
    w.show()
    exit(app.exec())
    # AccountAction.add_history(user_name='валера', link='123')
