import time
from datetime import timedelta
import os.path
import platform

import yt_dlp
from youtube_downloader.utils import get_referenced_folder, get_ffmpeg_path, download_latest_ffmpeg


def format_duration(seconds: float) -> str:
    return str(timedelta(seconds=seconds))


def format_size(size_bytes: float) -> str:
    """Convert size in bytes to human-readable format"""
    if not size_bytes:  # Handle zero or None size
        return ''
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}GB"


class ProgressHook:
    def __init__(self):
        self.progress = {
            'status': 'downloading',
            'percentage': '0%',
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'speed': 0,
            'filename': ''
        }

    def __call__(self, d):
        if d['status'] == 'downloading':
            # self.progress['status'] = 'downloading'
            self.progress['percentage'] = d.get('_percent_str', '0%').strip()
            self.progress['downloaded_bytes'] = d.get('downloaded_bytes', 0)
            self.progress['total_bytes'] = d.get('total_bytes', 0)
            self.progress['speed'] = d.get('speed', 0)
            self.progress['filename'] = d.get('filename', '')
        elif d['status'] == 'finished':
            self.progress['status'] = 'finished'
            self.progress['filename'] = d.get('filename', '')


class Downloader:
    def __init__(self, url: str):
        self.url: str = url
        self.progress_hook = ProgressHook()
        self.ytdlp_options: dict = {
            # 'quiet': True,
            'ffmpeg_location': get_ffmpeg_path(),
            'progress_hooks': [self.progress_hook],
        }
        self._youtubeDL = None
        self._info: dict = {}

    @property
    def youtubeDL(self):
        if not self._youtubeDL:
            self._youtubeDL = yt_dlp.YoutubeDL(self.ytdlp_options)
        return self._youtubeDL

    @property
    def info(self):
        if not self._info:
            self._info = self.youtubeDL.extract_info(self.url, download=False)
        return self._info

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
        return base_path

    def get_video_formats(self) -> list[dict]:
        formats = []
        for f in self.info.get('formats', []):
            if f.get('vcodec', 'none').startswith('avc'):
                if f.get('filesize', None):
                    formats.append({
                        'format_id': f['format_id'],
                        'resolution': f.get('height', 'N/A'),
                        'quality': ('High Quality' if f.get('height', 0) >= 720
                                    else 'Medium Quality' if f.get('height', 0) >= 480
                                    else 'Low Quality'),
                        'ext': f.get('ext', 'N/A'),
                        'filesize': format_size(f.get('filesize', 0)),
                        'vcodec': f.get('vcodec', 'none'),
                    })
        if not formats:
            for f in self.info.get('formats', []):
                if f.get('vcodec', 'none').startswith('avc'):
                    formats.append({
                        'format_id': f['format_id'],
                        'resolution': f.get('height', 'N/A'),
                        'quality': ('High Quality' if f.get('height', 0) >= 720
                                    else 'Medium Quality' if f.get('height', 0) >= 480
                                    else 'Low Quality'),
                        'ext': f.get('ext', 'N/A'),
                        'filesize': 0,
                        'vcodec': f.get('vcodec', 'none'),
                    })

        return formats

    def get_audio_formats(self) -> list[dict] | None:
        best_format = None
        for f in self.info.get('formats', []):
            if f.get('vcodec') == 'none' and f.get('acodec') != 'none' and f.get('abr', 0):
                if best_format is None:
                    best_format = f
                else:
                    best_format = max(
                        best_format, f, key=lambda x: x.get('abr', 0))
        if not best_format:
            # If no audio formats found, return the first available format
            for f in self.info.get('formats', []):
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    best_format = f
                    break

        return [{
            'format_id': best_format['format_id'],
            'abr': best_format.get('abr', 0),
            'quality': 'Low Quality' if best_format.get('abr', 0) < 128 else 'High Quality',
            'ext': best_format.get('ext', 'N/A'),
            'filesize': format_size(best_format.get('filesize', 0)),
            'acodec': best_format.get('acodec', 'none'),
        }]

    def get_thumbnail(self) -> str:
        """Get thumbnail URL"""
        return self.info.get('thumbnail', '')

    def get_video_info(self) -> dict:
        return {
            'title': self.info.get('title', 'Unknown Title'),
            'duration': format_duration(self.info.get('duration', 0)),
            'thumbnail': self.get_thumbnail(),
            'formats': self.get_video_formats(),
            'audio_formats': self.get_audio_formats()
        }

    def download(self, fmt: dict) -> str:
        """Download the video or audio based on the selected format.
        :param fmt: The format dictionary containing format details.
        :return: The downloaded file path."""
        # Determine if this is a video or audio format
        is_video = fmt.get('vcodec') != 'none'

        path = os.path.join(
            self.path, 'Video' if is_video else 'Audio', '%(title)s (%(height)sp).%(ext)s' if is_video else '%(title)s.%(ext)s')

        # Update options based on format type
        if is_video:
            video_format = fmt.get('format_id', 'bestvideo')
            self.ytdlp_options.update({
                'outtmpl': path,
                # Combine selected video with best audio
                'format': f'{video_format}+bestaudio',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'merge_output_format': 'mp4',
            })
        else:
            # Get the audio quality from the selected format
            # Default to 192kbps if not specified
            audio_quality = fmt.get('abr', 192)

            # Get metadata from the video info
            metadata = {
                'title': self.info.get('title', 'Unknown Title'),
                'artist': self.info.get('artists', [self.info.get('uploader', 'Unknown Artist')])[0],
                'album': self.info.get('album', self.info.get('title', 'Unknown Album')),
                # 'track': self.info.get('track', ''),
                'date': str(self.info.get('release_year', self.info.get('upload_date', '')[:4])),
                'description': self.info.get('description', ''),
                'comment': '',
            }

            self.ytdlp_options.update({
                'outtmpl': path,
                'format': fmt.get('format_id', 'bestaudio'),
                'writethumbnail': True,  # Download thumbnail
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': str(audio_quality),
                    },
                    {
                        'key': 'EmbedThumbnail',  # Embed thumbnail in the audio file
                    },
                    {
                        'key': 'FFmpegMetadata',  # Add metadata
                        'add_metadata': True,
                    },
                ],
                'postprocessor_args': [
                    '-metadata', f'title={metadata["title"]}',
                    '-metadata', f'artist={metadata["artist"]}',
                    '-metadata', f'album={metadata["album"]}',
                    # '-metadata', f'track={metadata["track"]}',
                    '-metadata', f'date={metadata["date"]}',
                    '-metadata', f'description={metadata["description"]}',
                    '-metadata', f'comment={metadata["comment"]}',
                ],
            })

        with yt_dlp.YoutubeDL(self.ytdlp_options) as ydl:
            path = ydl.prepare_filename(self.info)

            base_path = os.path.splitext(path)[0]
            if is_video:
                path = f"{base_path}.mp4"
            # For audio downloads, update the filename to .mp3
            else:
                path = f"{base_path}.mp3"

            if os.path.exists(path):
                return path

            ydl.download([self.url])

        current_time = time.time()

        # Update the file's modification time
        os.utime(path, (current_time, current_time))

        return path

    # @staticmethod
    # def progress_hook(d):
    #     if d['status'] == 'downloading':
    #         total = d.get('total_bytes', 0)
    #         downloaded = d['downloaded_bytes']
    #         percentage = downloaded / total * 100 if total else 0
    #         return (
    #             f"Downloading: {percentage:.2f}% at {d.get('speed', 'Unknown')} B/s, ETA: {d.get('eta', 'Unknown')}s")
    #     elif d['status'] == 'finished':
    #         return (f"Download completed: {d['filename']}")
    #     elif d['status'] == 'error':
    #         return ("An error occurred during the download.")
