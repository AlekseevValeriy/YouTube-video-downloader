from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QDialog

from json_reader import JsonReader

"""
Класс, который открывает окно гайдом по программе YoTuViLo 
"""


class Guide(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('guide.ui', self)
        self.left_button.clicked.connect(self.left)
        self.right_button.clicked.connect(self.right)
        self.current_page = 0
        slides = JsonReader.read_file('jsons/image_titles.json')
        self.pages = [slides[i] for i in slides]

        self.move(0)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.left()
        elif event.key() == Qt.Key_Right:
            self.right()

    def left(self):
        self.move(-1)

    def right(self):
        self.move(1)

    def move(self, number: int):
        self.current_page = (self.current_page + number) % len(self.pages)
        image, image_title = self.pages[self.current_page]
        self.image_label.setPixmap(QPixmap.fromImage(QImage(image)).scaled(600, 490))
        self.text_line.setText(image_title)
