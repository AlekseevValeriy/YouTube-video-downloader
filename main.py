import shutil
from sys import exit, argv
from tinytag import TinyTag


import requests
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QGuiApplication, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from pytube import YouTube, Playlist, Stream
import threading


class YouLoader(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi('design_cool.ui', self)
        self.link = ''
        self.type_status = 'video'
        self.format_status = 'video'
        self.line_status = 'wrong'
        self.stream_options = []
        self.p_progress = 0
        self.last_bytes = 0
        self.count_one = 0

        self.video_type_radio.clicked.connect(self.change_type)
        self.playlist_type_radio.clicked.connect(self.change_type)
        self.video_format_radio.clicked.connect(self.change_format)
        self.audio_format_radio.clicked.connect(self.change_format)
        self.paste_button.clicked.connect(self.paste_link)
        self.copy_button.clicked.connect(self.copy_link)
        self.link_line.editingFinished.connect(self.line_inspector_thread)
        self.choice_path_button.clicked.connect(self.select_path)
        self.load_button.clicked.connect(self.download_thread)

    def change_type(self) -> None:
        text = self.sender().text()
        if text == 'Видео':
            self.type_status = 'video'
        elif text == 'Плэйлист':
            self.type_status = 'playlist'
        self.line_inspector_thread()

    def change_format(self) -> None:
        text = self.sender().text()
        if text == 'Видео':
            self.format_status = 'video'
        elif text == 'Аудио':
            self.format_status = 'audio'
        self.line_inspector_thread()

    def paste_link(self) -> None:
        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data.hasText():
            self.link_line.setText(mime_data.text())

    def copy_link(self) -> None:
        text = self.link_line.text()
        if text:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)

    def display_line_status(self) -> None:
        if self.line_status == 'correct':
            self.line_status_label.setText('Верный формат ссылки')
            self.line_status_label.setStyleSheet("color: green;")
            if self.type_status == 'video' and self.title_line.text() != YouTube(self.link_line.text()).title:
                thread_metadata = threading.Thread(target=self.display_metadata_youtube_video)
                thread_qualities = threading.Thread(target=self.adding_qualities_video)
                thread_metadata.start()
                if self.quality_box.count():
                    self.quality_box.clear()
                thread_qualities.start()
            elif self.type_status == 'playlist' and self.title_line.text() != Playlist(self.link_line.text()).title:
                thread_metadata = threading.Thread(target=self.display_metadata_youtube_playlist)
                thread_qualities = threading.Thread(target=self.adding_qualities_playlist)
                thread_metadata.start()
                if self.quality_box.count():
                    self.quality_box.clear()
                thread_qualities.start()

        elif self.line_status == 'wrong':
            self.line_status_label.setText('Неверный формат ссылки')
            self.line_status_label.setStyleSheet("color: red;")
            self.clear_metadata()
            self.clear_qualities()

    def adding_qualities_video(self) -> None:
        if self.format_status == 'video':
            streams = YouTube(self.link_line.text()).streams.filter(progressive=True, type=self.format_status)
            self.quality_box.addItems([stream.resolution for stream in streams])
        elif self.format_status == 'audio':
            streams = YouTube(self.link_line.text()).streams.filter(type=self.format_status)
            self.quality_box.addItems([stream.abr for stream in streams])



    def adding_qualities_playlist(self) -> None:
        if self.format_status == 'video':
            streams = Playlist(self.link_line.text()).videos[0].streams.filter(progressive=True, type=self.format_status)
            self.quality_box.addItems([stream.resolution for stream in streams])
        elif self.format_status == 'audio':
            streams = Playlist(self.link_line.text()).videos[0].streams.filter(type=self.format_status)
            self.quality_box.addItems([stream.abr for stream in streams])

    def clear_qualities(self) -> None:
        self.quality_box.clear()

    def display_metadata_youtube_video(self) -> None:
        text = YouTube(self.link_line.text())
        self.title_line.setText(text.title)
        self.author_line.setText(text.author)
        self.additional_label_1.setText('Длина в сек.:')
        self.additional_line_1.setText(str(text.length))
        self.additional_label_2.setText('Дата загрузки:')
        self.additional_line_2.setText(str(text.publish_date))
        try:
            self.display_preview()
        except Exception as e:
            print(type(e).__name__, e)

    def display_preview(self) -> None:
        response = requests.get(YouTube(self.link_line.text()).thumbnail_url, stream=True)
        with open('video_preview.png', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response

        video_preview = QImage('video_preview.png')
        video_preview_size = [video_preview.width(), video_preview.height()]

        k = max(video_preview_size) / 150
        if video_preview_size[0] > video_preview_size[1]:
            video_preview_size = [150, int(video_preview_size[1] // k)]
        elif video_preview_size[0] < video_preview_size[1]:
            video_preview_size = [int(video_preview_size[0] // k), 150]
        else:
            video_preview_size = [150, 150]

        self.image_label.setPixmap(QPixmap.fromImage(video_preview).scaled(*video_preview_size))

    def display_metadata_youtube_playlist(self) -> None:
        if bool(self.image_label.pixmap()):
            self.clear_metadata()
        text = Playlist(self.link_line.text())
        self.title_line.setText(text.title)
        self.author_line.setText(text.owner)
        self.additional_label_1.setText('Количество:')
        self.additional_line_1.setText(str(text.length))
        self.additional_label_2.setText('Просмотры:')
        try:
            self.additional_line_2.setText(str(text.views))
        except ValueError:
            self.additional_line_2.setText(str(0))

    def clear_metadata(self) -> None:
        self.title_line.clear()
        self.author_line.clear()
        self.additional_label_1.setText('Доп. линия:')
        self.additional_line_1.clear()
        self.additional_label_2.setText('Доп. линия:')
        self.additional_line_2.clear()
        self.image_label.clear()

    def line_inspector_process(self) -> None:
        text = self.link_line.text()
        try:
            if self.type_status == 'video':
                YouTube(text)
            elif self.type_status == 'playlist':
                Playlist(text).title

            self.line_status = 'correct'
        except Exception:
            self.line_status = 'wrong'
        self.display_line_status()

    def line_inspector_thread(self):
        thread = threading.Thread(target=self.line_inspector_process)
        thread.start()

    def select_path(self) -> None:
        directory_string = QFileDialog.getExistingDirectory(self)
        if directory_string:
            self.path_line.setText(directory_string)
        print(directory_string)

    def on_progress(self, stream, chunk, bytes_remaining):
        if self.load_progress_bar.value() == 100:
            self.load_progress_bar.setValue(0)

        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        if self.last_bytes == 0:
            download_speed = total_size - bytes_remaining
        else:
            download_speed = self.last_bytes - bytes_remaining

        l_progress = int(bytes_downloaded / total_size * 100)
        if l_progress > self.p_progress:
            self.p_progress = l_progress
            self.load_progress_bar.setValue(l_progress)

            self.internet_speed_line.setText(f'{download_speed / (1024 ** 2):.2f} мб./сек.')
            self.remaining_time_line.setText(f'{int((bytes_remaining / download_speed) / 60)} мин. {int((bytes_remaining / download_speed) % 60)} сек.')
        self.last_bytes = bytes_remaining

    def on_complete_video(self, stream, path):
        self.quality_line.setText('1 / 1')
        self.p_progress = 0
        self.internet_speed_line.setText('0 мб./сек.')
        self.remaining_time_line.setText('0 мин. 0 сек.')
        # in the future
        # tag = TinyTag.get(path)
        # tags_text = [self.tag_line_1, self.tag_line_2, self.tag_line_3, self.tag_line_4, self.tag_line_5, self.tag_line_6]
        # tags = [self.tags_box_1, self.tags_box_2, self.tags_box_3, self.tags_box_4, self.tags_box_5, self.tags_box_6]
        # for text, tag_box in zip(tags_text, tags):
        #     if text.text():
        #         tag.


    def on_complete_playlist(self, stream, path):
        line = self.quality_line.text().split(' / ')
        if len(set(line)) == 1:
            self.count_one = 0
        self.quality_line.setText(f'{self.count_one} / {line[1]}')
        self.p_progress = 0
        self.internet_speed_line.setText('0 мб./сек.')
        self.remaining_time_line.setText('0 мин. 0 сек.')

    def download_process(self):
        if self.type_status == 'video':
            self.quality_line.setText('0 / 1')
            self.load_progress_bar.setValue(0)
            video = YouTube(self.link_line.text())
            video.register_on_progress_callback(self.on_progress)
            video.register_on_complete_callback(self.on_complete_video)
            if self.format_status == 'video':
                stream = video.streams.filter(progressive=True, resolution=self.quality_box.currentText(), type=self.format_status)
                stream[0].download(output_path=self.path_line.text())
            elif self.format_status == 'audio':
                stream = video.streams.filter(progressive=False, abr=self.quality_box.currentText(), type=self.format_status)
                print(stream)

                stream[0].download(output_path=self.path_line.text())

        elif self.type_status == 'playlist':
            playlist = Playlist(self.link_line.text())
            self.quality_line.setText(f'0 / {playlist.length}')
            for video in [YouTube(link) for link in playlist]:
                video.register_on_progress_callback(self.on_progress)
                video.register_on_complete_callback(self.on_complete_playlist)
                self.count_one += 1
                if self.format_status == 'video':
                    stream = video.streams.filter(progressive=True, resolution=self.quality_box.currentText(),
                                                  type=self.format_status)
                    stream[0].download(output_path=self.path_line.text())
                elif self.format_status == 'audio':
                    stream = video.streams.filter(progressive=False, abr=self.quality_box.currentText(),
                                                  type=self.format_status)
                    print(stream)
                    stream[0].download(output_path=self.path_line.text())


    def custom_hook(self, error):
        print(error)

    def download_thread(self):
        threading.excepthook = self.custom_hook
        thread = threading.Thread(target=self.download_process)
        thread.start()
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


if __name__ == '__main__':
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(argv)
    w = YouLoader()
    w.show()
    exit(app.exec())
