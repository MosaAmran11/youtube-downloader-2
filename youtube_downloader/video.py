import os.path

from .downloader import Downloader
from .utils import show_download_message, open_dir


class Video(Downloader):
    def __init__(self, url: str, resolution: str = '1080'):
        super().__init__(url)
        self.ytdlp_options.update({
            # 'format': f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
            'format': f'bestvideo[height<={resolution}]',
            'outtmpl': os.path.normpath(os.path.join(self.path, self.file_name))
        })

    @property
    def file_name(self):
        return f"{self.info['title']} ({self.info['resolution'].split('x')[0]}p).mp4"

    @property
    def path(self):
        return os.path.join(super().path, 'Video')

    def download(self):
        show_download_message()
        super().download()
        open_dir(os.path.join(self.path, self.file_name))
