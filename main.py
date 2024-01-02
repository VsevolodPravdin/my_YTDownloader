import sys
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, \
    QMessageBox, QFileDialog, QProgressBar
from PyQt5.QtCore import Qt
from pytube import YouTube


class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(200, 200, 800, 600)  # Увеличиваем размеры окна

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        # Применяем стили для темной темы
        self.setStyleSheet(
            "background-color: #333333; color: #FFFFFF; font-size: 18px;"
        )

        self.url_label = QLabel("Введите URL видео или плейлиста:")
        self.url_input = QLineEdit()
        self.layout.addWidget(self.url_label)
        self.layout.addWidget(self.url_input)

        self.resolution_label = QLabel("Выберите разрешение (оставьте пустым для максимального):")
        self.resolution_input = QLineEdit()
        self.layout.addWidget(self.resolution_label)
        self.layout.addWidget(self.resolution_input)

        self.path_label = QLabel("Выберите путь для сохранения:")
        self.path_input = QLineEdit()
        self.browse_button = QPushButton("Обзор...")
        self.browse_button.clicked.connect(self.browse_path)
        self.layout.addWidget(self.path_label)
        self.layout.addWidget(self.path_input)
        self.layout.addWidget(self.browse_button)

        self.download_button = QPushButton("Скачать")
        self.download_button.clicked.connect(self.download)
        self.layout.addWidget(self.download_button)

        self.progress_label = QLabel("Прогресс загрузки:")
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_label)
        self.layout.addWidget(self.progress_bar)

        self.central_widget.setLayout(self.layout)

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
        self.path_input.setText(path)

    def download(self):
        url = self.url_input.text()
        resolution = self.resolution_input.text() if self.resolution_input.text() else None
        output_path = self.path_input.text()

        if not url or not output_path:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите URL и выберите путь для сохранения.")
            return

        try:
            if 'playlist' in url.lower():
                self.download_youtube_playlist(url, output_path)
            else:
                self.download_youtube_video(url, output_path, resolution)
            QMessageBox.information(self, "Загрузка завершена", "Загрузка завершена!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def download_youtube_playlist(self, playlist_url, output_path):
        playlist = YouTube(playlist_url)
        total_videos = len(playlist.videos)
        for index, video in enumerate(playlist.videos):
            video.register_on_progress_callback(
                lambda stream, chunk, bytes_remaining: self.show_progress(stream, bytes_remaining))
            video_stream = video.streams.get_highest_resolution()
            video_stream.download(output_path)
            self.progress_bar.setValue(((index + 1) / total_videos) * 100)

    def download_youtube_video(self, video_url, output_path, resolution=None):
        try:
            yt = YouTube(video_url)
            video_id = self.extract_video_id(video_url)

            if not video_id:
                raise ValueError("Неверный URL видео")

            yt = YouTube('https://www.youtube.com/watch?v=' + video_id)
            yt.register_on_progress_callback(
                lambda stream, chunk, bytes_remaining: self.show_progress(stream, bytes_remaining))

            if resolution:
                video = yt.streams.filter(res=resolution).first()
            else:
                video = yt.streams.get_highest_resolution()

            video.download(output_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def show_progress(self, stream, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.progress_bar.setValue(int(percentage))

    def extract_video_id(self, url):
        video_id = None
        patterns = [
            r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})",
            r"^[a-zA-Z0-9_-]{11}$"
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                break
        return video_id


def run_app():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Используем стиль Fusion для поддержки тёмной темы
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")  # Подсказки

    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()
