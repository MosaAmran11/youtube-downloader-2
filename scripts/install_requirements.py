import os
import platform
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path


def install_ffmpeg():
    system = platform.system()
    ffmpeg_installed = shutil.which("ffmpeg")

    if ffmpeg_installed:
        print("FFmpeg is already installed.")
        return

    if system == "Windows":
        # Windows download URL
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        ffmpeg_zip_path = Path("ffmpeg.zip")
        ffmpeg_extract_dir = Path("ffmpeg")

        # Download and extract
        print("Downloading FFmpeg...")
        urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip_path)

        print("Extracting FFmpeg...")
        with zipfile.ZipFile(ffmpeg_zip_path, "r") as zip_ref:
            zip_ref.extractall(ffmpeg_extract_dir)

        # Find the bin directory inside extracted files
        ffmpeg_bin = ffmpeg_extract_dir / "ffmpeg-*-essentials_build" / "bin"
        os.environ["PATH"] += os.pathsep + str(ffmpeg_bin.resolve())

        # Clean up zip file
        ffmpeg_zip_path.unlink()

    elif system == "Linux":
        # Use apt on Debian-based systems
        try:
            print("Installing FFmpeg via apt...")
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"], check=True)
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

    # Verify FFmpeg installation
    if shutil.which("ffmpeg"):
        print("FFmpeg installed successfully.")
    else:
        print("Failed to install FFmpeg. Please try a manual installation.")


# Run the installation function
install_ffmpeg()
