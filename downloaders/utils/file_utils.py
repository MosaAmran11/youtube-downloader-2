import os
import platform
import re
from typing import Dict

from downloaders.utils import raise_on_error


def get_downloader_paths() -> Dict[str, str]:
    """Get download paths for different file types"""
    base_path = get_base_download_path()

    return {
        'home': base_path,
        'video': os.path.join(base_path, 'Video'),
        'audio': os.path.join(base_path, 'Audio'),
        'thumbnail': os.path.join(base_path, '.thumbnails'),
        'temp': os.path.join(base_path, '.temp'),
    }


def get_base_download_path() -> str:
    """Get the base download path for the application"""
    app_name = "YouTube Downloader"

    if platform.system() == 'Windows':
        downloads_path = get_windows_downloads_path()
    else:
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    return os.path.join(downloads_path, app_name)


def get_windows_downloads_path() -> str:
    """Get Windows Downloads folder path from registry"""
    try:
        import winreg as reg
        with reg.OpenKey(reg.HKEY_CURRENT_USER,
                         r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
            downloads_path, _ = reg.QueryValueEx(
                key, '{374DE290-123F-4565-9164-39C4925E467B}')
            return downloads_path
    except (ImportError, FileNotFoundError, OSError):
        # Fallback to default Downloads path
        return os.path.join(os.path.expanduser('~'), 'Downloads')


def ensure_directories_exist():
    """Create necessary directories if they don't exist"""
    paths = get_downloader_paths()
    for path in paths.values():
        os.makedirs(path, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()


def is_video_file(filename: str) -> bool:
    """Check if file is a video file"""
    video_extensions = {'.mp4', '.avi', '.mkv',
                        '.mov', '.wmv', '.flv', '.webm'}
    return get_file_extension(filename) in video_extensions


def is_audio_file(filename: str) -> bool:
    """Check if file is an audio file"""
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
    return get_file_extension(filename) in audio_extensions


@raise_on_error()
def safe_name(name: str, max_length: int = 255) -> str:
    """
    Sanitize a string to be safe for use as a filename on most file systems.
    Removes or replaces characters not allowed in file names.
    """
    if not isinstance(name, str):
        raise ValueError("name must be a string")
    if not max_length or not isinstance(max_length, int) or max_length <= 0:
        raise ValueError("max_length must be a positive integer")
    # Remove or replace invalid characters (Windows, macOS, Linux)
    # Invalid: \ / : * ? " < > | and control chars
    name = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', name)
    # Remove leading/trailing whitespace and dots
    name = name.strip().strip('.')
    # Collapse multiple underscores
    name = re.sub(r'_+', '_', name)
    # Limit length
    if len(name) > max_length:
        name = name[:max_length]
    # Fallback if name is empty
    if not name:
        name = "untitled"
    return name


@raise_on_error()
def prepare_output_template(format_obj: dict, is_video: bool = True) -> str:
    """Prepare output template based on file type"""
    if not isinstance(is_video, bool):
        raise ValueError("is_video must be a boolean value")
    filetype = 'video' if is_video else 'audio'
    abs_path = get_downloader_paths()[filetype]
    if is_video:
        return os.path.join(abs_path, f'{format_obj['title']} ({format_obj['height']}p).{format_obj["ext"]}')
    else:
        return os.path.join(abs_path, f'{format_obj['title']}.{format_obj["ext"]}')
