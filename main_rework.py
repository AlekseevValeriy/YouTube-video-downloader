import threading
import pytube.exceptions as exceptions

from sys import exit, argv
from time import sleep
from requests import get
from shutil import copyfileobj
from json_reader import JsonReader
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QGuiApplication, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from pytube import YouTube, Playlist
from datetime import datetime


class YoTuViLo(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('design_cool_rework.ui', self)
        self.TEST_FLAG = True
        self.errors_box = []
        self.errors_presets = JsonReader().read_file('errors_presets.json')
        self.flags_box = {'li_in_fl': True}
        self.file_characteristic = {'url': '', 'type': 'видео', 'format': 'видео'}
        self.paste_button.clicked.connect(self.paste_string)
        self.copy_button.clicked.connect(self.copy_string)
        self.type_box.currentTextChanged.connect(self.set_type)
        self.format_box.currentTextChanged.connect(self.set_format)

        # TODO MenuTools ->настройки -> проверка строки после изменения троки
        # TODO MenuTools ->настройки -> проверка строки после нажатия клавиши Enter
        self.link_line.editingFinished.connect(self.line_inspector_thread)

    def _error_inspector_flag_block(flag_name):
        def decorator_h(function):
            def decorator(self, *args, **kwargs):
                self.flags_box[flag_name] = False
                try:
                    function(self, *args, **kwargs)
                except Exception as error:
                    self.test_print(f'{type(error).__name__.title()} - {error}')
                    self.errors_box.append(f'{type(error).__name__.title()} - {error}')
                self.flags_box[flag_name] = True

            return decorator

        return decorator_h

    def _error_inspector_args(function):
        def error_inspector(self, *args, **kwargs):
            try:
                function(self, *args, **kwargs)
            except AssertionError as error:
                self.test_print(f'{type(error).__name__.title()} - {error}')
                self.errors_box.append(f'{type(error).__name__.title()} - {error}')
            except Exception as error:
                self.test_print(f'{type(error).__name__.title()} - {error}')
                self.errors_box.append(f'{type(error).__name__.title()} - {error}')

        return error_inspector

    def _error_inspector(function):
        def error_inspector(self):
            try:
                function(self)
            except AssertionError as error:
                self.test_print(f'{type(error).__name__.title()} - {error}')
                self.errors_box.append(f'{type(error).__name__.title()} - {error}')
            except Exception as error:
                self.test_print(f'{type(error).__name__.title()} - {error}')
                self.errors_box.append(f'{type(error).__name__.title()} - {error}')

        return error_inspector

    '''link_layout sector'''

    def set_type(self):
        self.file_characteristic['type'] = self.type_box.currentText()
        self.test_print(self.file_characteristic['type'])

    def set_format(self):
        self.file_characteristic['format'] = self.format_box.currentText()
        self.test_print(self.file_characteristic['format'])

    def set_url(self):
        self.file_characteristic['url'] = self.link_line.text()
        self.test_print(self.file_characteristic['url'])

    def clear_url(self):
        self.file_characteristic['url'] = ''
        self.test_print(self.file_characteristic['url'])

    def set_text(self, text: str, color: str):
        self.link_line_accuracy.setText(text)
        self.link_line_accuracy.setStyleSheet(f"color: {color};")
        # для line_inspector_process
        if color == 'red':
            self.clear_url()

    @_error_inspector
    def paste_string(self) -> None:
        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData()
        assert mime_data.hasText()
        self.link_line.setText(mime_data.text())
        self.line_inspector_thread()

    @_error_inspector
    def copy_string(self) -> None:
        link_string = self.link_line.text()
        assert 'https://www.youtube.com/' in link_string
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(link_string)

    @_error_inspector_args
    def line_inspector_process(self, link: str):
        try:
            self.type_box.setEnabled(False)
            self.paste_button.setEnabled(False)
            # self.work_test() # 5 секунд отдыха
            if self.file_characteristic['type'] == 'видео':
                assert YouTube(link)
                YouTube(link).check_availability()
            elif self.file_characteristic['type'] == 'плэйлист':
                assert Playlist(link)
            self.set_text('Верный формат ссылки', 'green')
            self.set_url()
            self.flags_box['li_in_fl'] = True
            self.display_metadata_thread()
        except Exception as error:
            self.type_box.setEnabled(True)
            self.paste_button.setEnabled(True)
            self.set_text(self.errors_presets.get(type(error).__name__, type(Exception()).__name__), 'red')
            self.clear_url()
            self.description_clear()
            self.preview_clear()
            raise error
        finally:
            self.flags_box['li_in_fl'] = True


    def line_inspector_thread(self):
        if bool(self.flags_box['li_in_fl']):
            self.flags_box['li_in_fl'] = False
            thread = threading.Thread(name='line_inspector_thread', target=self.line_inspector_process,
                                      args=(self.link_line.text(),))
            thread.start()

    '''tags_layout sector'''

    '''download_layout sector'''

    '''load_progress_layout sector'''

    '''description_and_preview_layout sector'''

    @_error_inspector
    def display_metadata_process(self):
        if self.file_characteristic['type'] == 'видео':
            self.download_url()
            self.preview_set()
            self.description_video_set()
        elif self.file_characteristic['type'] == 'плэйлист':
            self.description_playlist_set()
        self.type_box.setEnabled(True)
        self.paste_button.setEnabled(True)

    @_error_inspector
    def download_url(self):
        response = get(YouTube(self.file_characteristic['url']).thumbnail_url, stream=True)
        with open('video_preview.png', 'wb') as out_file:
            copyfileobj(response.raw, out_file)
        del response

    @_error_inspector
    def preview_set(self):
        video_preview = QImage('video_preview.png')
        width = video_preview.width()
        height = video_preview.height()

        if width > height:
            video_preview_size = [150, int(f'{height / (width / 150):.0f}')]
        elif width < height:
            video_preview_size = [int(f'{width / (height / 150):.0f}'), 150]
        else:
            video_preview_size = [150, 150]

        self.image_label.setPixmap(QPixmap.fromImage(video_preview).scaled(*video_preview_size))

    def preview_clear(self):
        self.image_label.clear()

    @_error_inspector
    def description_video_set(self):
        video = YouTube(self.file_characteristic['url'])
        self.title_line.setText(video.title)
        self.author_line.setText(video.author)
        self.additional_label_1.setText('Длина в сек.:')
        self.additional_line_1.setText(str(video.length))
        self.additional_label_2.setText('Дата загрузки:')
        format = '%d.%m.%y'
        self.additional_line_2.setText(video.publish_date.strftime(format))

    @_error_inspector
    def description_playlist_set(self):
        self.preview_clear()
        playlist = Playlist(self.file_characteristic['url'])
        self.title_line.setText(playlist.title)
        self.author_line.setText(playlist.owner)
        self.additional_label_1.setText('Количество:')
        self.additional_line_1.setText(str(playlist.length))
        self.additional_label_2.setText('Просмотры:')
        try:
            self.additional_line_2.setText(str(playlist.views))
        except ValueError:
            self.additional_line_2.setText(str(0))

    def description_clear(self):
        self.title_line.clear()
        self.author_line.clear()
        self.additional_label_1.setText('Доп. линия:')
        self.additional_line_1.clear()
        self.additional_label_2.setText('Доп. линия:')
        self.additional_line_2.clear()

    def display_metadata_thread(self):
        if bool(self.flags_box['li_in_fl']) and bool(self.file_characteristic['url']):
            thread = threading.Thread(name='display_metadata_thread', target=self.display_metadata_process)
            thread.start()

    """statusBar sector"""

    def test_print(self, text):
        if self.TEST_FLAG:
            print(text)

    def work_test(self):
        sleep(5)

    def closeEvent(self, event):
        print(', '.join(self.errors_box))


if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(argv)
    w = YoTuViLo()
    w.show()
    exit(app.exec())
