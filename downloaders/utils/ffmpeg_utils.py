import os
import re
import shutil
import platform
import tempfile
import requests
import urllib.request
import subprocess
import sys
import zipfile
from pathlib import Path


def get_system_ffmpeg_path() -> str:
    """Get FFmpeg executable path from system PATH"""
    return shutil.which('ffmpeg')


def get_ffmpeg_install_dir() -> str:
    """Get the appropriate installation directory for FFmpeg"""
    system = platform.system()

    if system == "Windows":
        # Use user's AppData or Program Files
        program_files = os.environ.get('LOCALAPPDATA', 'C:\\Program Files')
        return os.path.join(program_files, 'Programs', 'FFmpeg')
    else:  # Linux or macOS
        # Use /usr/local/bin or ~/bin
        user_bin = os.path.expanduser('~/bin')
        if not os.path.exists(user_bin):
            os.makedirs(user_bin, exist_ok=True)
        return user_bin


def add_to_path(ffmpeg_dir: str) -> bool:
    """Add FFmpeg directory to system PATH"""
    system = platform.system()

    try:
        if system == "Windows":
            return _add_to_windows_path(ffmpeg_dir)
        else:
            return _add_to_unix_path(ffmpeg_dir)
    except Exception as e:
        print(f"Warning: Could not add FFmpeg to PATH: {e}")
        return False


def _add_to_windows_path(ffmpeg_dir: str) -> bool:
    """Add directory to Windows PATH environment variable"""
    try:
        import winreg as reg

        # Get current PATH
        with reg.OpenKey(reg.HKEY_CURRENT_USER,
                         r'Environment', 0, reg.KEY_READ | reg.KEY_WRITE) as key:
            try:
                current_path, _ = reg.QueryValueEx(key, 'Path')
            except FileNotFoundError:
                current_path = ''

            # Check if already in PATH
            if ffmpeg_dir in current_path:
                print("FFmpeg already in PATH")
                return True

            # Add to PATH
            new_path = current_path + ';' + ffmpeg_dir if current_path else ffmpeg_dir
            reg.SetValueEx(key, 'Path', 0, reg.REG_EXPAND_SZ, new_path)

            # Also update current session
            os.environ['PATH'] = new_path + ';' + os.environ.get('PATH', '')

            print(f"Added {ffmpeg_dir} to Windows PATH")
            return True

    except Exception as e:
        print(f"Could not update Windows PATH: {e}")
        return False


def _add_to_unix_path(ffmpeg_dir: str) -> bool:
    """Add directory to Unix PATH environment variable"""
    try:
        # Determine shell profile file
        home = os.path.expanduser('~')
        shell = os.environ.get('SHELL', '/bin/bash')

        if 'bash' in shell:
            profile_file = os.path.join(home, '.bashrc')
        elif 'zsh' in shell:
            profile_file = os.path.join(home, '.zshrc')
        else:
            profile_file = os.path.join(home, '.profile')

        # Check if already in PATH
        if os.path.exists(profile_file):
            with open(profile_file, 'r') as f:
                content = f.read()
                if ffmpeg_dir in content:
                    print("FFmpeg already in PATH")
                    return True

        # Add to shell profile
        path_export = f'\n# FFmpeg path\nexport PATH="$PATH:{ffmpeg_dir}"\n'

        with open(profile_file, 'a') as f:
            f.write(path_export)

        # Update current session
        os.environ['PATH'] = os.environ.get('PATH', '') + ':' + ffmpeg_dir

        print(f"Added {ffmpeg_dir} to {profile_file}")
        print("Please restart your terminal or run 'source ~/.bashrc' to apply changes")
        return True

    except Exception as e:
        print(f"Could not update Unix PATH: {e}")
        return False


def get_ffmpeg_path() -> str:
    """Get FFmpeg executable path"""
    # First check if ffmpeg is in system PATH
    ffmpeg_path = get_system_ffmpeg_path()
    if ffmpeg_path:
        return ffmpeg_path

    # Check for bundled FFmpeg (fallback)
    base_path = get_ffmpeg_install_dir()
    if os.path.exists(base_path):
        for entry in os.listdir(base_path):
            if os.path.isdir(os.path.join(base_path, entry)) and entry.startswith('ffmpeg-'):
                ffmpeg_dir = entry
                bin_path = os.path.join(base_path, ffmpeg_dir, 'bin')
                if os.path.exists(bin_path):
                    for file in os.listdir(bin_path):
                        if file.startswith('ffmpeg'):
                            return os.path.normpath(os.path.join(bin_path, file))

    return None


def download_ffmpeg(install_dir: str = None) -> str:
    """Download and extract FFmpeg to system directory"""
    install_dir = install_dir or get_ffmpeg_install_dir()

    system = platform.system()

    if system == "Windows":
        # Windows download URL
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

        # Download and extract
        print("Downloading FFmpeg...")
        try:
            response = requests.get(ffmpeg_url, stream=True)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                archive_path = temp_file.name

        except Exception as e:
            print(f"Failed to download FFmpeg: {e}")
            return None

        # Extract archive content
        temp_extract_dir_path = tempfile.mkdtemp()

        try:
            print("Extracting archive...")
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_dir_path)

            # Find the extracted FFmpeg directory (e.g.: ffmpeg-7.0.1-essentials_build)
            extracted_dir_name = next(os.walk(temp_extract_dir_path))[1][0]
            extracted_dir_path = os.path.join(
                temp_extract_dir_path, extracted_dir_name)

            # Create installation directory
            os.makedirs(install_dir, exist_ok=True)

            # Move FFmpeg to installation directory
            shutil.move(extracted_dir_path, install_dir)
            print(f"FFmpeg installed at {install_dir}")

            bin_dir = os.path.join(install_dir, extracted_dir_name, 'bin')
            return bin_dir

        finally:
            os.remove(archive_path)
            shutil.rmtree(temp_extract_dir_path)

    elif system == "Linux":
        # Use apt on Debian-based systems
        try:
            print("Installing FFmpeg via apt...")
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install",
                           "-y", "ffmpeg"], check=True)
        except Exception as e:
            print("Failed to install FFmpeg via apt:", e)
            print("Please install FFmpeg manually.")

    elif system == "Darwin":  # macOS
        try:
            print("Installing FFmpeg via Homebrew...")
            subprocess.run(["brew", "install", "ffmpeg"], check=True)
        except Exception as e:
            print("Failed to install FFmpeg via Homebrew:", e)
            print("Please install FFmpeg manually.")


def ensure_ffmpeg_available() -> bool:
    """Ensure FFmpeg is available, download if necessary"""
    # First check if already available
    if get_system_ffmpeg_path():
        print("FFmpeg found in system PATH")
        return True

    print("FFmpeg not found. Attempting to download and install...")

    # Download and install FFmpeg
    install_dir = download_ffmpeg()
    if not install_dir:
        print("Failed to download FFmpeg")
        return False

    # Add to PATH
    if add_to_path(install_dir):
        print("FFmpeg successfully installed and added to PATH")
        return True
    else:
        print("FFmpeg installed but could not be added to PATH")
        print(f"You may need to manually add {install_dir} to your PATH")
        return False


def verify_ffmpeg_installation() -> bool:
    """Verify that FFmpeg is properly installed and accessible"""
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("FFmpeg verification successful")
            return True
        else:
            print("FFmpeg verification failed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"FFmpeg verification error: {e}")
        return False
