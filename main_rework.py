import threading
from shutil import copyfileobj
from sys import exit, argv
from time import sleep

# import mutagen
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QGuiApplication, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from pytube import YouTube, Playlist
from requests import get

from json_reader import JsonReader
from credits import Credits
from guide import Guide


class YoTuViLo(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('design_cool_rework.ui', self)
        self.TEST_FLAG = True
        self.MESSAGE_TIME = 15
        self.errors_box = []
        self.errors_presets = JsonReader().read_file('jsons\\errors_presets.json')
        self.settings_presets = JsonReader().read_file('jsons\\settings_presets.json')
        self.flags_box = {'li_in_fl': True, 'qu_bo_fl': True, 'pr_di_fl': True}
        self.file_characteristic = {'url': '', 'type': 'видео', 'format': 'видео'}
        self.cache_box = {'last_downloaded_bytes': 0, 'p_progress': 0, 'quality_line': [0, 0]}

        self.paste_button.clicked.connect(self.paste_string)
        self.copy_button.clicked.connect(self.copy_string)
        self.type_box.currentTextChanged.connect(self.set_type)
        self.format_box.currentTextChanged.connect(self.set_format)
        self.quality_box.currentTextChanged.connect(self.set_quality)
        self.choice_path_button.clicked.connect(self.choice_path)
        self.load_button.clicked.connect(self.load_thread)

        self.link_line.editingFinished.connect(self.line_inspector_thread)

        self.fast_inspector.triggered.connect(lambda a: self.change_inspector_speed('fast'))
        self.slow_inspector.triggered.connect(lambda a: self.change_inspector_speed('slow'))
        self.about_author.triggered.connect(self.open_credits)
        self.open_guide.triggered.connect(self.open_guidee)

        index = self.type_box.findText(self.settings_presets['video_type'])
        self.type_box.setCurrentIndex(index)

        index = self.format_box.findText(self.settings_presets['video_format'])
        self.format_box.setCurrentIndex(index)

    """menuBar sector"""

    def change_inspector_speed(self, speed):
        self.test_print(speed)
        self.settings_presets['quality_inspector'] = speed

    def open_credits(self):
        w = Credits()
        w.show()
        w.exec_()

    def open_guidee(self):
        w = Guide()
        w.show()
        w.exec_()

    """decorators sector"""

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
        self.settings_presets['video_type'] = self.type_box.currentText()
        self.test_print(self.settings_presets['video_type'])
        self.test_print(self.file_characteristic['type'])

    def set_format(self):
        self.file_characteristic['format'] = self.format_box.currentText()
        self.settings_presets['video_format'] = self.format_box.currentText()
        self.test_print(self.settings_presets['video_format'])
        self.test_print(self.file_characteristic['format'])

    def set_quality(self):
        if self.file_characteristic['format'] == 'видео':
            self.settings_presets['video_quality_res'] = self.quality_box.currentText()
        elif self.file_characteristic['format'] == 'аудио':
            self.settings_presets['video_quality_res'] = self.quality_box.currentText()
        self.test_print(self.settings_presets['video_quality_res'])
        self.test_print(self.quality_box.currentText())

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

    @_error_inspector
    def line_inspector_process(self):
        try:
            self.interface_set_disable()
            self.cache_box['quality_line'] = [0, 0]
            self.set_quality_line_values()
            self.load_progress_bar.setValue(0)
            link = self.link_line.text()
            # self.work_test() # 5 секунд отдыха
            if self.file_characteristic['type'] == 'видео':
                assert YouTube(link)
                YouTube(link).check_availability()
            elif self.file_characteristic['type'] == 'плэйлист':
                assert Playlist(link)
            self.set_text('Верный формат ссылки', 'green')
            self.set_url()
            self.flags_box['li_in_fl'] = True
            self.flags_box['qu_bo_fl'] = False
            self.flags_box['pr_di_fl'] = False
            self.display_metadata_thread()
            self.set_quality_thread()
        except Exception as error:
            self.interface_set_enable()
            self.set_text(
                self.errors_presets.get(type(error).__name__, self.errors_presets[type(Exception()).__name__]), 'red')
            self.clear_url()
            self.description_clear()
            self.preview_clear()
            self.clear_qualities()
            raise error
        finally:
            self.flags_box['li_in_fl'] = True

    def line_inspector_thread(self):
        if bool(self.flags_box['li_in_fl']):
            self.flags_box['li_in_fl'] = False
            thread = threading.Thread(name='line_inspector_thread', target=self.line_inspector_process)
            thread.start()

    '''tags_layout sector'''
    # TODO надо сделать через mutagen, там есть mp4, ogg, нужно ещё weba и что-то ещё

    '''download_layout sector'''

    @_error_inspector
    def load_process(self):
        try:
            self.cache_box['quality_line'] = [0, 0]
            self.set_quality_line_values()
            self.interface_set_disable()
            if self.file_characteristic['type'] == 'видео':
                video = YouTube(self.file_characteristic['url'], on_progress_callback=self.on_progress,
                                on_complete_callback=self.on_complete)
                self.cache_box['quality_line'] = [0, 1]
                self.set_quality_line_values()
                self.clear_load_progress_bar()
                if self.file_characteristic['format'] == 'видео':
                    stream = video.streams.filter(progressive=True, type='video', res=self.quality_box.currentText())
                elif self.file_characteristic['format'] == 'аудио':
                    stream = video.streams.filter(type='audio', abr=self.quality_box.currentText())
                stream.first().download(output_path=self.path_line.text())


            elif self.file_characteristic['type'] == 'плэйлист':
                playlist = Playlist(self.file_characteristic['url'])
                self.cache_box['quality_line'] = [0, playlist.length]
                self.set_quality_line_values()
                for video in playlist.videos:
                    video.register_on_progress_callback(self.on_progress)
                    video.register_on_complete_callback(self.on_complete)
                    self.clear_load_progress_bar()
                    if self.file_characteristic['format'] == 'видео':
                        stream = video.streams.filter(progressive=True, type='video',
                                                      res=self.quality_box.currentText())
                    elif self.file_characteristic['format'] == 'аудио':
                        stream = video.streams.filter(progressive=False, type='audio',
                                                      abr=self.quality_box.currentText())
                    stream.first().download(output_path=self.path_line.text())
        except Exception as error:
            raise error
        finally:
            self.interface_set_enable()

    def load_thread(self):
        if bool(self.flags_box['li_in_fl']) and bool(self.file_characteristic['url']):
            thread = threading.Thread(name='load_thread', target=self.load_process)
            thread.start()

    @_error_inspector
    def choice_path(self):
        path = QFileDialog.getExistingDirectory(self)
        if path:
            self.path_line.setText(path)
        self.test_print(path)

    def set_quality_process(self):
        def get_qualities(video: YouTube) -> list:
            if self.file_characteristic['format'] == 'видео':
                streams = video.streams.filter(progressive=True, type='video')
                return [stream.resolution for stream in streams]
            elif self.file_characteristic['format'] == 'аудио':
                streams = video.streams.filter(type='audio')
                return [stream.abr for stream in streams]

        try:
            if self.file_characteristic['type'] == 'видео':
                video = YouTube(self.file_characteristic['url'])
                qualities = get_qualities(video)
            elif self.file_characteristic['type'] == 'плэйлист':
                if self.settings_presets['quality_inspector'] == 'slow':
                    self.test_print('slow_inspector')
                    videos = Playlist(self.file_characteristic['url']).videos
                    qualities_dict = {}
                    for video in videos:
                        for quality in get_qualities(video):
                            if quality not in qualities_dict:
                                qualities_dict[quality] = 0
                            qualities_dict[quality] += 1

                    quantity_qualities = {}
                    for quality in qualities_dict:
                        if qualities_dict[quality] not in quantity_qualities:
                            quantity_qualities[qualities_dict[quality]] = []
                        quantity_qualities[qualities_dict[quality]].append(quality)
                    qualities = quantity_qualities[max(quantity_qualities)]
                elif self.settings_presets['quality_inspector'] == 'fast':
                    self.test_print('fast_inspector')
                    videos = Playlist(self.file_characteristic['url']).videos
                    qualities = get_qualities(videos[0])
            self.clear_qualities()
            self.quality_box.addItems(qualities)

            if self.file_characteristic['format'] == 'видео':
                index = self.quality_box.findText(self.settings_presets['video_quality_res'])
            elif self.file_characteristic['format'] == 'аудио':
                index = self.quality_box.findText(self.settings_presets['video_quality_abr'])
            self.quality_box.setCurrentIndex(index)
        except Exception as error:
            raise error
        finally:
            if self.flags_box['pr_di_fl']:
                self.interface_set_enable()
            self.flags_box['qu_bo_fl'] = True

    def clear_qualities(self):
        if self.quality_box.count() != 0:
            self.quality_box.clear()

    def set_quality_thread(self):
        if bool(self.flags_box['li_in_fl']) and bool(self.file_characteristic['url']):
            thread = threading.Thread(name='set_quality_thread', target=self.set_quality_process)
            thread.start()

    '''load_progress_layout sector'''

    @_error_inspector_args
    def on_progress(self, stream, chunk, bytes_remaining):
        print(1, bytes_remaining)
        #  Какая-то хрень - не работает нормально отслеживание
        # после тильта надо попробовать убрать маску или если не выйдет , то проанализировать main.py
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining

        if self.cache_box['last_downloaded_bytes'] == 0:
            download_speed = total_size - bytes_remaining
        else:
            download_speed = self.cache_box['last_downloaded_bytes'] - bytes_remaining

        l_progress = int((bytes_downloaded / total_size) * 100)
        if l_progress > self.cache_box['p_progress']:
            self.cache_box['p_progress'] = l_progress
            self.load_progress_bar.setValue(l_progress)

            self.internet_speed_line.setText(self.mask_text(f'{download_speed / (1024 ** 2):.0f}', 'r'))
            minutes = self.mask_text((f'{bytes_remaining / download_speed / 60:.0f}'), 'r')
            seconds = self.mask_text(f'{bytes_remaining / download_speed % 60:.0f}', 'r')
            self.remaining_time_line.setText(minutes + seconds)

        self.cache_box['last_downloaded_bytes'] = bytes_remaining

    def on_complete(self, stream, path):
        self.internet_speed_line.clear()
        self.remaining_time_line.clear()
        self.cache_box['quality_line'][0] += 1
        self.set_quality_line_values()

    def set_quality_line_values(self):
        n_1, n_2 = self.cache_box['quality_line']
        self.quality_line.setText(self.mask_text(n_1, 'r') + self.mask_text(n_2, 'l'))

    def mask_text(self, text, side: str) -> str:
        text = str(text)
        if len(text) < 4:
            empty_text = ' ' * (4 - len(text))
            if side == 'r':
                return empty_text + text
            elif side == 'l':
                return text + empty_text
        return text

    def clear_load_progress_bar(self):
        self.load_progress_bar.setValue(0)

    '''description_and_preview_layout sector'''

    @_error_inspector
    def display_metadata_process(self):
        try:
            if self.file_characteristic['type'] == 'видео':
                self.download_url()
                self.preview_set()
                self.description_video_set()
            elif self.file_characteristic['type'] == 'плэйлист':
                self.description_playlist_set()
        except Exception as error:
            raise error
        finally:
            if self.flags_box['qu_bo_fl']:
                self.interface_set_enable()
        self.flags_box['pr_di_fl'] = True

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
            video_preview_size = [int(f'{width / (height / 150):.0f}'), 150]
        elif width < height:
            video_preview_size = [int(f'{height / (width / 150):.0f}'), 150]
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

    # TODO Странно, после выставления времени больше 1 он перестаёт показывать значения
    def set_message(self, message):
        pass
        # self.statusBar().showMessage("this is status bar")

    """other sector"""

    def interface_set_enable(self):
        self.type_box.setEnabled(True)
        self.paste_button.setEnabled(True)
        self.link_line.setEnabled(True)
        self.format_box.setEnabled(True)
        self.choice_path_button.setEnabled(True)
        self.path_line.setEnabled(True)
        self.download_layout.setEnabled(True)
        self.load_button.setEnabled(True)
        self.quality_box.setEnabled(True)

    def interface_set_disable(self):
        self.type_box.setEnabled(False)
        self.paste_button.setEnabled(False)
        self.link_line.setEnabled(False)
        self.format_box.setEnabled(False)
        self.choice_path_button.setEnabled(False)
        self.path_line.setEnabled(False)
        self.download_layout.setEnabled(False)
        self.load_button.setEnabled(False)
        self.quality_box.setEnabled(False)

    def test_print(self, text):
        if self.TEST_FLAG:
            print(text)

    def work_test(self):
        sleep(5)

    def closeEvent(self, event):
        self.test_print('exit')
        self.test_print(', '.join(self.errors_box))
        JsonReader().write_file(self.settings_presets, 'jsons\\settings_presets.json')


if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(argv)
    w = YoTuViLo()
    w.show()
    exit(app.exec())
