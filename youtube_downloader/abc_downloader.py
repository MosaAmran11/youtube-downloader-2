import os
import platform
from abc import ABC, abstractmethod

from youtube_downloader.utils import get_referenced_folder


class Downloader(ABC):
    def __init__(self, url: str):
        self.url = url
        self.params: dict  # Initialized with None
        self._paths: dict | None = None

    @property
    def paths(self) -> dict[str, str]:
        if not self._paths:
            app_name: str = "Youtube Downloader MAA"
            if platform.system() == 'Windows':
                base_path = os.path.join(
                    get_referenced_folder('Downloads'),
                    app_name)
            else:
                base_path = os.path.join(
                    os.getenv("HOME"),
                    'Downloads',
                    app_name)
            self._paths = {
                'home': base_path,
                'video': os.path.join(base_path, 'Video'),  # Directory for video files
                'audio': os.path.join(base_path, 'Audio'),  # Directory for audio files
                'subtitle': os.path.join(base_path, 'Subtitles'),  # Directory for subtitle files
                'temp': os.path.join(base_path, '.temp'),  # Temporary download path for fragmented files
                'thumbnail': os.path.join(base_path, '.thumbnails'),  # Directory for thumbnail images
            }
        return self._paths

    @paths.setter
    def paths(self, value):
        self.paths = value

    @abstractmethod
    def download_video(self, url: str = None, resolution: str = 'best', format: str = 'mp4') -> str:
        """Download the video and return the downloaded file path"""
        pass

    @abstractmethod
    def download_audio(self, url: str = None, format: str = 'mp3') -> str:
        """Download the audio and return the downloaded file path"""
        pass

    @abstractmethod
    def get_available_formats(self, url: str = None) -> list[str]:
        pass
