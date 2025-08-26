import os
import platform
import subprocess

platform_type = platform.system()

def open_file_location(filepath: str) -> bool:
    """Open file location in file explorer"""
    try:
        if is_windows():
            os.system(f'explorer /select,"{os.path.normpath(filepath)}"')
        elif is_macos:  # macOS
            os.system(f'open "{os.path.dirname(filepath)}"')
        else:  # Linux
            os.system(f'xdg-open "{os.path.dirname(filepath)}"')
        return True
    except Exception:
        return False


def open_file(filepath: str) -> bool:
    """Open file with default application"""
    try:
        if is_windows():
            os.startfile(filepath)
        elif is_linux():  # macOS
            subprocess.run(["open", filepath])
        else:  # Linux
            subprocess.run(["xdg-open", filepath])
        return True
    except Exception:
        return False


def get_system_info() -> dict:
    """Get system information"""
    return {
        'system': platform_type,
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor()
    }


def is_windows() -> bool:
    """Check if running on Windows"""
    return platform_type == "Windows"


def is_macos() -> bool:
    """Check if running on macOS"""
    return platform_type == "Darwin"


def is_linux() -> bool:
    """Check if running on Linux"""
    return platform_type == "Linux"
