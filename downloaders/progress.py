from typing import Dict


class ProgressHook:
    """Track download progress"""

    def __init__(self):
        self.progress = {
            'status': 'downloading',
            'percentage': '0%',
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'speed': 0,
            'filename': ''
        }

    def __call__(self, d: Dict):
        """Update progress from yt-dlp callback"""
        if d['status'] == 'downloading':
            self.progress['percentage'] = "{:.2f}%".format(
                d.get('_percent', 0))
            self.progress['downloaded_bytes'] = d.get('downloaded_bytes', 0)
            self.progress['total_bytes'] = d.get('total_bytes', 0)
            self.progress['speed'] = d.get('speed', 0)
            self.progress['filename'] = d.get('filename', '')
        elif d['status'] == 'finished':
            self.progress['status'] = 'finished'
            self.progress['filename'] = d.get('filename', '')

    def reset(self):
        """Reset progress to initial state"""
        self.progress = {
            'status': 'downloading',
            'percentage': '0%',
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'speed': 0,
            'filename': ''
        }

    def set_error(self, error_message: str):
        """Set error state"""
        self.progress['status'] = 'error'
        self.progress['error'] = error_message
