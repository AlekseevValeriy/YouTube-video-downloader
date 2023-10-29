
from sys import exit, argv
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog


class Credits(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('credits.ui', self)

if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(argv)
    w = Credits()
    w.show()
    exit(app.exec())
