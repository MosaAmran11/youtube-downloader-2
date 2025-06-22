import os

import requests
from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3
from yt_dlp import YoutubeDL

from downloaders.utils import CLEAR, RED, RESET, BLUE, BIN
from downloaders.abc_downloader import Downloader
from concurrent.futures import ThreadPoolExecutor, as_completed

"""
A concrete implementation of the Downloader class for downloading YouTube videos.
"""


class YoutubeDownloader(Downloader):
    def __init__(self, url: str):
        super().__init__(url=url)
        self.params: dict = {
            'quiet': True,
            'write_subs': True,
            'outtmpl': '%(title)s.%(ext)s',
            'ffmpeg_location': BIN,
            # 'external_downloader': 'ffmpeg',
        }

    def download_video(self, url: str = None, resolution: str = '1080', format: str = 'mp4') -> str:
        ydl_opts = dict(self.params)  # Copy the params to avoid modifying the original params
        ydl_opts.update({
            'paths': {
                'home': self.paths.get('video'),
                'temp': self.paths.get('temp'),
                'subtitle': self.paths.get('subtitle'),
                'thumbnail': self.paths.get('thumbnail'),
            },
            'format': f'bestvideo[height={resolution}]+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': format,
            }],
        })

        with YoutubeDL(ydl_opts) as ytd:
            info = ytd.extract_info(url or self.url, download=True)

            video_file = ytd.prepare_filename(info).replace(".webm", f".{format}").replace(".mp4", f".{format}")
            return os.path.join(self.paths.get('video'), video_file)

    def download_audio(self, url: str = None, format: str = 'mp3') -> str:
        ydl_opts = dict(self.params)  # Copy the params to avoid modifying the original params
        ydl_opts.update({
            'paths': {
                'home': self.paths.get('audio'),
                'temp': self.paths.get('temp'),
                'subtitle': self.paths.get('subtitle'),
                'thumbnail': self.paths.get('thumbnail'),
            },
            'format': f'[abr>130]/bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format,
            }],
        })

        with YoutubeDL(ydl_opts) as ytd:
            info = ytd.extract_info(url or self.url, download=True)

            audio_filename = ytd.prepare_filename(info).replace(".webm", f".{format}").replace(".mp4", f".{format}")
            thumbnail_url = info.get('thumbnail', None)
            if thumbnail_url:
                self._embed_thumbnail(audio_filename, thumbnail_url)
            return os.path.join(self.paths.get('audio'), audio_filename)

    def download_playlist(self, url: str = None, download_type: str = 'video', resolution: str = 'best',
                          format: str = 'mp4', max_workers: int = 3):
        ydl_opts = dict(self.params)  # Copy the params to avoid modifying the original params
        ydl_opts.update({
            'extract_flat': True,  # Extract playlist metadata without downloading
            'paths': {
                'home': self.paths.get(download_type),
                'temp': self.paths.get('temp'),
                'subtitle': self.paths.get('subtitle'),
                'thumbnail': self.paths.get('thumbnail'),
            },
        })

        with YoutubeDL(ydl_opts) as ytd:
            playlist_info = ytd.extract_info(url or self.url, download=False)
            if not playlist_info.get('entries'):
                print("This is not a playlist or the playlist is empty.")
                return

            print(f"Downloading playlist: {playlist_info.get('title', 'Unknown')}")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for entry in playlist_info['entries']:
                entry_url = entry.get('url')
                print(f"Queueing download: {entry['title']}")

                if download_type == 'audio':
                    future = executor.submit(self.download_audio, entry_url, format)
                elif download_type == 'video':
                    future = executor.submit(self.download_video, entry_url, resolution, format)
                else:
                    print(f"Unsupported download type: {download_type}. Please choose 'audio' or 'video'.")
                    continue
                futures.append(future)

            # Wait for all threads to complete
            for future in as_completed(futures):
                try:
                    future.result()  # Ensure any exceptions are raised
                except Exception as e:
                    print(f"An error occurred: {e}")

    def get_available_formats(self, url: str = None) -> list[str]:
        with YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('formats', [])
            # return [f"{f['format']} ({f['ext']})" for f in formats]

    def _embed_thumbnail(self, audio_filename: str, thumbnail_url: str):
        # Download the thumbnail image
        thumbnail_data = requests.get(thumbnail_url).content
        thumbnail_path = os.path.join(self.paths.get('thumbnail'), 'thumbnail.jpg')
        os.makedirs(self.paths.get('thumbnail'), exist_ok=True)
        with open(thumbnail_path, 'wb') as f:
            f.write(thumbnail_data)

        # Embed the thumbnail image into the audio file
        try:
            audio = MP3(audio_filename, ID3=ID3)
            audio.tags.add(APIC(
                encoding=3,  # 3 = utf-8
                mime='image/jpeg',  # MIME type of the image
                type=3,  # 3 = cover image
                desc='Cover',
                data=open(thumbnail_path, 'rb').read()
            ))
            audio.save()
        except error:
            # If the file has no existing ID3 tags, add them
            audio = MP3(audio_filename)
            audio.add_tags()
            audio.tags.add(APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=open(thumbnail_path, 'rb').read()
            ))
            audio.save()

        # Clean up the downloaded thumbnail image
        os.remove(thumbnail_path)

    @staticmethod
    def progress_hook(info):
        os.system(CLEAR)
        if info['status'] == 'downloading':
            total = info.get('total_bytes', 0)
            downloaded = info['downloaded_bytes']
            percentage = downloaded / total * 100 if total else 0
            print(
                f"Downloading: {percentage:.2f}% at {info.get('speed', 'Unknown')} B/s, ETA: {info.get('eta', 'Unknown')}s")

        elif info['status'] == 'finished':
            print(BLUE, f"\tDownload completed: {info['filename']}", RESET, sep='')

        elif info['status'] == 'error':
            print(RED, "\tAn error occurred during the download.", RESET, sep='')
