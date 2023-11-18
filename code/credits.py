from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

"""
Класс, который открывает окно с заслугами
"""


class Credits(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('credits.ui', self)
