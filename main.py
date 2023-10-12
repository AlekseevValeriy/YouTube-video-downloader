from pytube import YouTube
import sys
import shutil

import requests
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QImage



class YouLoader(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.link = 'https://www.youtube.com/watch?v=IlQ9BLV2Mm0'
        uic.loadUi('design.ui', self)
        self.pushButton.clicked.connect(self.download)
        self.pushButton_2.clicked.connect(self.display)

    def errors_trapper(func):
        def fun(self):
            try:
                func(self)
            except Exception as exception:
                print(exception)
        return fun

    # @errors_trapper
    def download(self):
        YouTube(self.link).streams.get_lowest_resolution().download()

    @errors_trapper
    def display(self):
        self.author_label.setText(YouTube(self.link).author)
        self.title_label.setText(YouTube(self.link).thumbnail_url)
        image = QImage(self.download_image(YouTube(self.link).thumbnail_url))
        self.preview.setPixmap(QPixmap.fromImage(image))

    def download_image(self, image_link: str) -> str:
        url = image_link
        image_name = 'img.png'
        response = requests.get(url, stream=True)
        with open(image_name, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        return image_name



if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    w = YouLoader()
    w.show()
    sys.exit(app.exec())
