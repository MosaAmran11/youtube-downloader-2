from datetime import timedelta
import os.path
import platform

import yt_dlp
from youtube_downloader.utils import get_referenced_folder, get_ffmpeg_path, download_latest_ffmpeg


def format_duration(seconds):
    return str(timedelta(seconds=seconds))


class Downloader:
    def __init__(self, url: str):
        self.url: str = url
        self.ytdlp_options: dict = {
            'format': 'best',  # Default to best quality
            'quiet': True,
            'outtmpl': self.path,
            'ffmpeg_location': get_ffmpeg_path(),
            'progress_hooks': [self.progress_hook],
        }
        self.info: dict = yt_dlp.YoutubeDL(
            self.ytdlp_options).extract_info(url, download=False)

    @property
    def path(self):
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
        return os.path.normpath(base_path)

    def get_video_formats(self) -> list[dict]:
        formats = []
        for f in self.info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
                formats.append(f)
        return formats

    def get_audio_formats(self) -> list[dict]:
        formats = []
        for f in self.info.get('formats', []):
            if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                formats.append(f)
        return formats

    def get_thumbnail(self) -> str:
        return self.info.get('thumbnail', '')

    def get_video_info(self) -> dict:
        return {
            'title': self.info.get('title', 'Unknown Title'),
            'duration': format_duration(self.info.get('duration', 0)),
            'thumbnail': self.get_thumbnail(),
            'formats': self.get_video_formats(),
            'audio_formats': self.get_audio_formats()
        }

    def download(self, format: str = 'bestvideo+bestaudio') -> str:
        # print(self.ytdlp_options['outtmpl'])
        if not os.path.exists(self.ytdlp_options['outtmpl']):
            with yt_dlp.YoutubeDL(self.ytdlp_options) as ydl:
                ydl.download([self.url])
        # print(f"Download completed for URL: {self.url}")
        return self.path

    @staticmethod
    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes', 0)
            downloaded = d['downloaded_bytes']
            percentage = downloaded / total * 100 if total else 0
            return (
                f"Downloading: {percentage:.2f}% at {d.get('speed', 'Unknown')} B/s, ETA: {d.get('eta', 'Unknown')}s")
        elif d['status'] == 'finished':
            return (f"Download completed: {d['filename']}")
        elif d['status'] == 'error':
            return ("An error occurred during the download.")
