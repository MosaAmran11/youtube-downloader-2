import threading
from typing import Dict, Optional
from downloaders.utils import raise_on_error
from downloaders.utils.file_utils import prepare_output_template
from downloaders.youtube import YouTubeDownloader
from app.utils.validators import is_valid_youtube_url
import os


class DownloadService:
    """Service for managing download operations"""

    def __init__(self):
        self.current_downloader: Optional[YouTubeDownloader] = None
        self.download_thread_obj: Optional[threading.Thread] = None
        self.file_path: Optional[str] = None

    @raise_on_error()
    def create_downloader(self, url: str) -> YouTubeDownloader:
        """Create a new downloader instance"""
        if not is_valid_youtube_url(url):
            raise ValueError("Invalid YouTube URL")

        self.current_downloader = YouTubeDownloader(url)
        return self.current_downloader

    @raise_on_error()
    def get_video_info(self, url: str) -> Dict:
        """Get video information for the given URL"""
        try:
            downloader = self.create_downloader(url)
            return downloader.get_video_info()
        except Exception as e:
            raise Exception(f"Could not fetch video information: {str(e)}")

    @raise_on_error()
    def start_download(self, url: str, format_id: str) -> Dict:
        """Start a download with the specified format"""
        if not self.current_downloader:
            self.create_downloader(url)

        # Find the format object
        format_obj = self._find_format(format_id)
        if not format_obj:
            raise ValueError("Selected format not found")

        format_obj.update({
            'title': self.current_downloader.info.get('title', 'Unknown Title'),
        })

        is_video = format_obj.get('vcodec') != 'none'

        # Reset progress
        self.current_downloader.progress_hook.reset()

        outtmpl = prepare_output_template(format_obj, is_video)
        self.file_path = os.path.splitext(
            outtmpl)[0] + ('.mp4' if is_video else '.mp3')

        if not os.path.exists(self.file_path):
            # Start download in background thread
            def download_thread():
                try:
                    self.current_downloader.download(format_obj)
                    if not self.file_path or not os.path.exists(self.file_path):
                        raise FileNotFoundError("Downloaded file not found")
                except Exception as e:
                    self.current_downloader.progress_hook.set_error(str(e))

            # Start the download thread
            self.download_thread_obj = threading.Thread(target=download_thread)
            self.download_thread_obj.daemon = True
            self.download_thread_obj.start()

        return {'status': 'started', 'filename': self.file_path}

    def get_progress(self) -> Dict:
        """Get current download progress"""
        if not self.current_downloader:
            return {'status': 'not_started'}

        progress = self.current_downloader.progress_hook.progress.copy()

        # Update status if thread is not alive
        if not self.download_thread_obj.is_alive():
            # if progress['status'] == 'downloading':
            progress['filename'] = self.file_path
            progress['status'] = 'done'

        return progress

    @raise_on_error()
    def _find_format(self, format_id: str) -> Optional[Dict]:
        """Find format object by format ID"""
        if not self.current_downloader:
            raise ValueError("No downloader instance available")

        # Search in video formats
        for fmt in self.current_downloader.info.get('formats', []):
            if fmt.get('format_id') == format_id:
                return fmt

        return None

    # def is_downloading(self) -> bool:
    #     """Check if a download is currently in progress"""
    #     return (self.download_thread_obj and
    #             self.download_thread_obj.is_alive() and
    #             self.current_downloader and
    #             self.current_downloader.progress_hook.progress['status'] == 'downloading')
