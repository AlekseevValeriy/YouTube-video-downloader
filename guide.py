from sys import exit, argv

from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QDialog

from json_reader import JsonReader


class Guide(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('guide.ui', self)
        self.left_button.clicked.connect(self.left)
        self.right_button.clicked.connect(self.right)
        self.current_page = 0
        slides = JsonReader().read_file('jsons\\images_titles.json')
        self.pages = [slides[i] for i in slides]

        self.move(0)

    def left(self):
        self.move(-1)

    def right(self):
        self.move(1)

    def move(self, number: int):
        self.current_page = (self.current_page + number) % len(self.pages)
        image, image_title = self.pages[self.current_page]
        self.image_label.setPixmap(QPixmap.fromImage(QImage(image)).scaled(600, 490))
        self.text_line.setText(image_title)


if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(argv)
    w = Guide()
    w.show()
    exit(app.exec())
