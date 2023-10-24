import threading
from sys import exit, argv
from time import sleep

from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication, QMainWindow
from pytube import YouTube, Playlist
import pytube.exceptions as exceptions


class YoTuViLo(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('design_cool_rework.ui', self)
        self.errors_box = []
        self.flags_box = {'li_in_fl': True}
        self.file_characteristic = {'url': '', 'type': 'video', 'format': 'video'}
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
                    print(f'{type(error).__name__.title()} - {error}')
                    self.errors_box.append(f'{type(error).__name__.title()} - {error}')
                self.flags_box[flag_name] = True

            return decorator

        return decorator_h

    def _error_inspector_args(function):
        def error_inspector(self, *args, **kwargs):
            try:
                function(self, *args, **kwargs)
            except AssertionError as error:
                print(f'{type(error).__name__.title()} - {error}')
                self.errors_box.append(f'{type(error).__name__.title()} - {error}')
            except Exception as error:
                print(f'{type(error).__name__.title()} - {error}')
                self.errors_box.append(f'{type(error).__name__.title()} - {error}')

        return error_inspector

    def _error_inspector(function):
        def error_inspector(self):
            try:
                function(self)
            except AssertionError as error:
                print(f'{type(error).__name__.title()} - {error}')
                self.errors_box.append(f'{type(error).__name__.title()} - {error}')
            except Exception as error:
                print(f'{type(error).__name__.title()} - {error}')
                self.errors_box.append(f'{type(error).__name__.title()} - {error}')

        return error_inspector

    '''link_layout sector'''

    def set_type(self):
        self.file_characteristic['type'] = self.type_box.currentText()
        print(self.file_characteristic['type'])

    def set_format(self):
        self.file_characteristic['format'] = self.format_box.currentText()
        print(self.file_characteristic['format'])

    def set_url(self):
        self.file_characteristic['url'] = self.link_line.text()
        print(self.file_characteristic['url'])

    def clear_url(self):
        self.file_characteristic['url'] = ''
        print(self.file_characteristic['url'])

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

    @_error_inspector_flag_block('li_in_fl')
    def line_inspector_process(self, link: str):
        try:
            self.type_box.setEnabled(False)
            self.paste_button.setEnabled(False)
            self.work_test() # 5 секунд отдыха
            if self.file_characteristic['type'] == 'video':
                assert YouTube(link)
                YouTube(link).check_availability()
            elif self.file_characteristic['type'] == 'playlist':
                assert Playlist(link)
            self.set_text('Верный формат ссылки', 'green')
        except Exception as error:
            error_text = 'Неверный формат ссылки'
            self.set_text(error_text, 'red')
            raise error
        finally:
            self.type_box.setEnabled(True)
            self.paste_button.setEnabled(True)

    def line_inspector_thread(self):
        if bool(self.flags_box['li_in_fl']):
            thread = threading.Thread(name='line_inspector_thread', target=self.line_inspector_process,
                                      args=(self.link_line.text(),))
            thread.start()

    '''tags_layout sector'''

    '''download_layout sector'''

    '''load_progress_layout sector'''

    '''description_and_preview_layout sector'''


    @_error_inspector
    def display_metadata_process(self):
        pass

    def display_metadata_thread(self):
        if bool(self.flags_box['li_in_fl']) and bool(self.file_characteristic['url']):
            thread = threading.Thread(name='display_metadata_thread', target=self.display_metadata_process)
            thread.start()

    """statusBar sector"""

    # TODO из self.display_metadata_process() выводить сообщения о ошибках в видео


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
