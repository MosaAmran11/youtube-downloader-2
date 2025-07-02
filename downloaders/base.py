from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from downloaders.progress import ProgressHook
from yt_dlp import YoutubeDL


class BaseDownloader(ABC):
    """Abstract base class for all downloaders"""

    def __init__(self, url: str):
        self.url = url
        self.progress_hook = ProgressHook()
        self.youtube_dl_options: Dict = {}
        self._youtube_dl: Optional[YoutubeDL] = None
        self._info: Dict = {}

    @property
    def youtube_dl(self) -> YoutubeDL:
        """Lazy initialization of yt-dlp instance"""
        """Return the yt-dlp instance for downloading"""
        if not self._youtube_dl:
            self._youtube_dl = YoutubeDL(self.youtube_dl_options)
        return self._youtube_dl

    @youtube_dl.setter
    def youtube_dl(self, value: YoutubeDL):
        """Set the yt-dlp instance"""
        if isinstance(value, YoutubeDL):
            self._youtube_dl = value
        else:
            raise ValueError(f"Expected yt_dlp.YoutubeDL instance, got {type(value).__name__}")

    @property
    def info(self) -> Dict:
        """Get video information"""
        if not self._info:
            self._info = self.youtube_dl.extract_info(self.url, download=False) or {}
        return self._info

    @info.setter
    def info(self, value: Dict):
        """Set video information"""
        if isinstance(value, dict):
            self._info = value
        else:
            raise ValueError(f"Info must be a dictionary, got {type(value).__name__}")

    @abstractmethod
    def get_video_info(self) -> Dict:
        """Get formatted video information for display"""
        pass

    @abstractmethod
    def download(self, format_obj: Dict) -> str:
        """Download the video/audio with specified format"""
        pass

    def get_video_formats(self) -> List[Dict]:
        """Get available video formats"""
        raise NotImplementedError

    def get_audio_formats(self) -> List[Dict]:
        """Get available audio formats"""
        raise NotImplementedError
