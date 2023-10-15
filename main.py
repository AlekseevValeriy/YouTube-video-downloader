import sys

from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication, QMainWindow
from pytube import YouTube, Playlist


class YouLoader(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('design_cool.ui', self)
        self.link = 'https://www.youtube.com/watch?v=mj8g_bJWyXQ&list=LL&index=4'
        self.type_status = 'video'
        self.format_status = 'video'
        self.line_status = 'wrong'

        self.video_type_radio.clicked.connect(self.change_type)
        self.playlist_type_radio.clicked.connect(self.change_type)
        self.video_format_radio.clicked.connect(self.change_format)
        self.audio_format_radio.clicked.connect(self.change_format)
        self.paste_button.clicked.connect(self.paste_link)
        self.copy_button.clicked.connect(self.copy_link)
        self.link_line.editingFinished.connect(self.line_inspector)

    def change_type(self) -> None:
        text = self.sender().text()
        if text == 'Видео':
            self.type_status = 'video'
        elif text == 'Плэйлист':
            self.type_status = 'playlist'
        self.line_inspector()

    def change_format(self) -> None:
        text = self.sender().text()
        if text == 'Видео':
            self.format_status = 'video'
        elif text == 'Аудио':
            self.format_status = 'audio'
        self.line_inspector()

    def paste_link(self) -> None:
        clipboard = QGuiApplication.clipboard()
        mimeData = clipboard.mimeData()
        if mimeData.hasText():
            self.link_line.setText(mimeData.text())

    def copy_link(self) -> None:
        text = self.link_line.text()
        if text:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)

    def display_line_status(self) -> None:
        if self.line_status == 'correct':
            self.line_status_label.setText('Верный формат ссылки')
            self.line_status_label.setStyleSheet("color: green;")
            self.display_metadata_youtube()
        elif self.line_status == 'wrong':
            self.line_status_label.setText('Неверный формат ссылки')
            self.line_status_label.setStyleSheet("color: red;")
            self.clear_metadata()

    def display_metadata_youtube(self) -> None:
        text: YouTube = YouTube(self.link_line.text())
        self.title_line.setText(text.title)
        self.author_line.setText(text.author)
        self.additional_line_1.setText(str(text.length))
        self.additional_line_2.setText(str(text.publish_date))

    def clear_metadata(self) -> None:
        self.title_line.clear()
        self.author_line.clear()
        self.additional_line_1.clear()
        self.additional_line_2.clear()

    def line_inspector(self) -> None:
        text = self.link_line.text()
        try:
            if self.type_status == 'video':
                YouTube(text)
            elif self.type_status == 'playlist':
                # TODO проблема - метод length может тормозить программу при быстрой смене ссылки
                Playlist(text).length
            self.line_status = 'correct'
        except Exception as e:
            self.line_status = 'wrong'
        self.display_line_status()

    # def errors_trapper(func):
    #     def fun(self):
    #         try:
    #             func(self)
    #         except Exception as exception:
    #             print(exception)
    #     return fun
    #
    # # @errors_trapper
    # def download(self):
    #     YouTube(self.link).streams.get_lowest_resolution().download()
    #
    # @errors_trapper
    # def display(self):
    #     self.author_label.setText(YouTube(self.link).author)
    #     self.title_label.setText(YouTube(self.link).thumbnail_url)
    #     image = QImage(self.download_image(YouTube(self.link).thumbnail_url))
    #     self.preview.setPixmap(QPixmap.fromImage(image))


if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    w = YouLoader()
    w.show()
    sys.exit(app.exec())
