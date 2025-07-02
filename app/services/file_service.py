import os
from downloaders.utils.platform_utils import open_file, open_file_location


class FileService:
    """Service for handling file operations"""

    @staticmethod
    def open_file_location(filepath: str) -> dict[str, str]:
        """Open file location in file explorer"""
        try:
            # Convert URL-encoded path to absolute path
            abs_path = os.path.abspath(filepath)

            if open_file_location(abs_path):
                return {'status': 'success'}
            else:
                return {'error': 'Failed to open file location'}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def open_file(filepath: str) -> dict[str, str]:
        """Open file with default application"""
        try:
            # Convert URL-encoded path to absolute path
            abs_path = os.path.abspath(filepath)

            if open_file(abs_path):
                return {'status': 'success'}
            else:
                return {'error': 'Failed to open file'}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def file_exists(filepath: str) -> bool:
        """Check if file exists"""
        try:
            abs_path = os.path.abspath(filepath)
            return os.path.exists(abs_path)
        except Exception:
            return False

    @staticmethod
    def get_file_info(filepath: str) -> dict:
        """Get file information"""
        try:
            abs_path = os.path.abspath(filepath)
            if not os.path.exists(abs_path):
                return {'error': 'File not found'}

            stat = os.stat(abs_path)
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'path': abs_path,
                'filename': os.path.basename(abs_path)
            }
        except Exception as e:
            return {'error': str(e)}
