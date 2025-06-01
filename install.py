import platform
import subprocess
import sys


def install_requirements():
    """Install the required packages system-wide."""
    system = platform.system()

    if system == "Linux":
        # Update package list
        subprocess.run("sudo apt update".split())

        # Install system packages
        subprocess.run(
            "sudo apt install python3-flask python3-requests python3-mutagen ffmpeg".split())

        # Install yt-dlp system-wide
        subprocess.run(
            "sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp".split())
        subprocess.run("sudo chmod a+rx /usr/local/bin/yt-dlp".split())

    elif system == "Windows":
        # Install all requirements system-wide using pip
        subprocess.run(
            "pip install -r requirements.txt".split())
    else:  # macOS
        # Install all requirements system-wide using pip
        subprocess.run(
            "sudo pip3 install -r requirements.txt".split())


if __name__ == "__main__":
    install_requirements()
