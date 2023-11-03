from sys import exit, argv

from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog


class AccountEnter(QDialog):
    def __init__(self, window_title):
        super().__init__()
        uic.loadUi('account_enter.ui', self)
        self.setWindowTitle(window_title)
        self.button.clicked.connect(self.enter_in_db)
        self.successful_login = False
        self.name = ''
        self.password = ''

    def enter_in_db(self):
        # здесь будет подключение к бд
        print(self.name_line.text())
        print(self.password_line.text())
        if self.name_line.text() and self.password_line.text():
            self.successful_login = True
            self.name = self.name_line.text()
            self.password = self.password_line.text()



if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(argv)
    w = AccountEnter('test')
    w.show()
    exit(app.exec())
