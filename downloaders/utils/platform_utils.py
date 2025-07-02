import os
import platform
import subprocess


def open_file_location(filepath: str) -> bool:
    """Open file location in file explorer"""
    try:
        if platform.system() == "Windows":
            os.system(f'explorer /select,"{os.path.normpath(filepath)}"')
        elif platform.system() == "Darwin":  # macOS
            os.system(f'open "{os.path.dirname(filepath)}"')
        else:  # Linux
            os.system(f'xdg-open "{os.path.dirname(filepath)}"')
        return True
    except Exception:
        return False


def open_file(filepath: str) -> bool:
    """Open file with default application"""
    try:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", filepath])
        else:  # Linux
            subprocess.run(["xdg-open", filepath])
        return True
    except Exception:
        return False


def get_system_info() -> dict:
    """Get system information"""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor()
    }


def is_windows() -> bool:
    """Check if running on Windows"""
    return platform.system() == "Windows"


def is_macos() -> bool:
    """Check if running on macOS"""
    return platform.system() == "Darwin"


def is_linux() -> bool:
    """Check if running on Linux"""
    return platform.system() == "Linux"
