import os
import yt_dlp
from typing import Dict, List
from downloaders.base import BaseDownloader
from downloaders.utils import raise_on_error
from downloaders.utils.ffmpeg_utils import get_ffmpeg_path
from downloaders.utils.file_utils import downloader_paths, prepare_output_template
from app.utils.formatters import format_duration, format_size


class YouTubeDownloader(BaseDownloader):
    """YouTube video/audio downloader using yt-dlp"""

    def __init__(self, url: str):
        super().__init__(url)
        self._setup_options()

    def _setup_options(self):
        """Setup yt-dlp options"""
        self.youtube_dl_options = {
            'paths': {
                'temp': downloader_paths()['temp'],
                'thumbnail': downloader_paths()['thumbnail']
            },
            'ffmpeg_location': get_ffmpeg_path(),
            'progress_hooks': [self.progress_hook],
        }

    @raise_on_error()
    def _filter_formats(self, is_video: bool = True) -> List[Dict]:
        """Filter formats to avoid duplicates based on quality"""
        if not isinstance(is_video, bool):
            raise ValueError("is_video must be a boolean value")

        format_qualities: Dict[int, Dict] = {}  # { height: fmt }
        CODEC = {1: 'vcodec', 0: 'acodec'}
        QUALITY = {1: 'height', 0: 'abr'}

        for f in self.info.get('formats', []):
            if f.get(CODEC[int(is_video)], 'none') != 'none' and f.get(CODEC[int(not is_video)], 'none') == 'none':

                if (f.get(QUALITY[int(is_video)], 0) or 0) not in format_qualities:
                    format_qualities[f.get(QUALITY[int(is_video)], 0) or 0] = f

                else:
                    if (not format_qualities[f.get(QUALITY[int(is_video)], 0) or 0].get('filesize', None) and
                            f.get('filesize', None)):
                        format_qualities[f.get(
                            QUALITY[int(is_video)], 0) or 0] = f

        return [fmt for fmt in format_qualities.values()]

    def get_video_formats(self) -> List[Dict]:
        """Get available video formats"""
        formats = []
        for f in self._filter_formats():
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

        return formats

    def get_audio_formats(self) -> List[Dict]:
        """Get available audio formats"""
        formats = []
        for f in self._filter_formats(False):
            formats.append({
                'format_id': f['format_id'],
                'abr': f.get('abr', 0),
                'quality': 'High Quality' if (f.get('abr', 0) or 0) >= 128 else 'Low Quality',
                'ext': f.get('ext', 'N/A'),
                'filesize': format_size(f.get('filesize', 0)),
                'acodec': f.get('acodec', 'none'),
            })

        return formats

    def get_thumbnail(self) -> Dict:
        """Get the best thumbnail for the video"""
        thumbnails = self.info.get('thumbnails', [])
        if thumbnails:
            # Prefer square thumbnails
            square_thumbnails = [
                t for t in thumbnails
                if t.get('width', 0) == t.get('height', 1)
            ]

            if square_thumbnails:
                # Return the highest resolution square thumbnail
                return max(square_thumbnails, key=lambda t: t.get('height', 0))

        # Fallback to default thumbnail
        return {'url': self.info.get('thumbnail', '')}

    def get_video_info(self) -> Dict:
        """Get formatted video information for display"""
        return {
            'title': self.info.get('title', 'Unknown Title'),
            'duration': format_duration(
                self.info.get('duration_string', self.info.get('duration', 0))),
            'thumbnail': self.get_thumbnail().get('url', ''),
            'formats': self.get_video_formats(),
            'audio_formats': self.get_audio_formats()
        }

    def download(self, format_obj: Dict) -> str:
        """Download the video/audio with specified format"""
        is_video = format_obj.get('vcodec') != 'none'
        format_obj.update({
            'title': self.info.get('title', 'Unknown Title'),
        })

        # Setup output template
        outtmpl = prepare_output_template(
            format_obj=format_obj, is_video=is_video)

        # Update options for download
        download_options = self.youtube_dl_options.copy()
        download_options.update({
            'outtmpl': {'default': outtmpl},
        })

        if is_video:
            video_format = format_obj.get('format_id', 'bestvideo')
            download_options.update({
                'format': f'{video_format}+bestaudio',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'merge_output_format': 'mp4',
                'postprocessor_args': [
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                ],
            })
        else:
            download_options.update({
                'format': format_obj.get('format_id', 'bestaudio'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })

        # Reset progress and download
        self.progress_hook.reset()
        with yt_dlp.YoutubeDL(download_options) as ydl:
            ydl.download([self.url])

        final_path = os.path.splitext(
            outtmpl)[0] + ('.mp4' if is_video else '.mp3')
        self.progress_hook.progress['filename'] = final_path

        # Return the downloaded file path
        return final_path

    def _get_quality_label(self, height: int) -> str:
        """Get quality label based on video height"""
        if height >= 720:
            return 'High Quality'
        elif height >= 480:
            return 'Medium Quality'
        else:
            return 'Low Quality'
