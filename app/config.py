import os
from downloaders.utils.file_utils import get_base_download_path


class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

    # Download settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB max file size
    DOWNLOAD_FOLDER = get_base_download_path()

    # FFmpeg settings
    FFMPEG_PATH = None  # Will be auto-detected

    # Threading settings
    MAX_DOWNLOAD_THREADS = 3
