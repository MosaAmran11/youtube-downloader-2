from setuptools import setup, find_packages

setup(
    name="youtube_downloader",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "yt-dlp",
        "ffmpeg-python",
    ],
    python_requires=">=3.6",
)
