import threading
from typing import Dict, Optional
from downloaders.youtube import YouTubeDownloader
from app.utils.validators import is_valid_youtube_url
import os


class DownloadService:
    """Service for managing download operations"""

    def __init__(self):
        self.current_downloader: Optional[YouTubeDownloader] = None
        self.download_thread: Optional[threading.Thread] = None

    def create_downloader(self, url: str) -> YouTubeDownloader:
        """Create a new downloader instance"""
        if not is_valid_youtube_url(url):
            raise ValueError("Invalid YouTube URL")

        self.current_downloader = YouTubeDownloader(url)
        return self.current_downloader

    def get_video_info(self, url: str) -> Dict:
        """Get video information for the given URL"""
        try:
            downloader = self.create_downloader(url)
            return downloader.get_video_info()
        except Exception as e:
            raise Exception(f"Could not fetch video information: {str(e)}")

    def start_download(self, url: str, format_id: str) -> Dict:
        """Start a download with the specified format"""
        if not self.current_downloader:
            self.current_downloader = YouTubeDownloader(url)

        # Find the format object
        format_obj = self._find_format(format_id)
        if not format_obj:
            raise ValueError("Selected format not found")

        # Reset progress
        self.current_downloader.progress_hook.reset()

        # Start download in background thread
        def download_thread():
            try:
                file_path = self.current_downloader.download(format_obj)
                if file_path and os.path.exists(file_path):
                    self.current_downloader.progress_hook.progress['status'] = 'finished'
                    self.current_downloader.progress_hook.progress['filename'] = file_path
                else:
                    self.current_downloader.progress_hook.set_error(
                        'File not found after download')
            except Exception as e:
                self.current_downloader.progress_hook.set_error(str(e))

        # Start the download thread
        self.download_thread = threading.Thread(target=download_thread)
        self.download_thread.daemon = True
        self.download_thread.start()

        return {'status': 'started'}

    def get_progress(self) -> Dict:
        """Get current download progress"""
        if not self.current_downloader:
            return {'status': 'not_started'}

        progress = self.current_downloader.progress_hook.progress.copy()

        # Update status if thread is not alive
        if self.download_thread and not self.download_thread.is_alive():
            if progress['status'] == 'downloading':
                progress['status'] = 'finished'

        return progress

    def _find_format(self, format_id: str) -> Optional[Dict]:
        """Find format object by format ID"""
        if not self.current_downloader:
            return None

        # Search in video formats
        for fmt in self.current_downloader.info.get('formats', []):
            if fmt.get('format_id') == format_id:
                return fmt

        return None

    def is_downloading(self) -> bool:
        """Check if a download is currently in progress"""
        return (self.download_thread and
                self.download_thread.is_alive() and
                self.current_downloader and
                self.current_downloader.progress_hook.progress['status'] == 'downloading')
