# YouTube Downloader

A cross-platform YouTube video/audio downloader with a web-based GUI, powered by Flask and yt-dlp.

## ⚠️ Disclaim

This tool is intended for personal and educational use only.
Downloading copyrighted content without permission is against [YouTube's Terms of Service](https://www.youtube.com/static?template=terms).
The author is not responsible for any misuse of this tool.

## Features

- Download YouTube videos and audio in various formats and qualities (Not support Playlists yet)
- Simple web interface for entering URLs and selecting formats
- Progress bar and download status updates
- Automatic FFmpeg setup (Windows/Linux)
- Open downloaded files or their location directly from the UI
- Metadata and thumbnail embedding for audio downloads

## Installation

### 🪟 Windows Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/MosaAmran11/youtube_downloader.git
   cd youtube-downloader-2
   ```

   If you do not have Git installed, Download the repository from [Here](https://github.com/MosaAmran11/youtube-downloader-2/archive/refs/heads/main.zip). Then, extract the files and enter to `youtube-downloader-2-main` directory.

2. Run the installer:

   ```bash
   python install.py
   ```

### 🐧 Linux Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/MosaAmran11/youtube_downloader.git
   cd youtube-downloader-2
   ```

2. Run the installer:

   You can simply run `install.py` file to install all requirements automatically, OR run the following commands to install manually:

   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv
   python3 -m venv venv
   source ./venv/bin/activate
   python3 -m pip install -r requirements.txt
   ```

## Usage

1. Start the server:

   ***1. On Windows***

   ```cmd
   python main.py
   ```

   ***2. On Linux***

   ```bash
   source venv/bin/activate
   python3 main.py
   ```

2. Open your browser and go to [http://localhost:5000](http://localhost:5000)
3. Paste a YouTube URL, get info, and choose your download format.

## Project Structure

- `main.py` — Flask web server and main entry point
- `youtube_downloader/` — Core downloader logic and utilities
- `static/` — Frontend JS and CSS
- `templates/` — HTML templates
- `scripts/` — Helper scripts for setup and requirements
- `tests/` — Unit and integration tests

## Requirements

See [requirements.txt](requirements.txt). Main dependencies:

- Flask
- yt-dlp
- requests
- mutagen

## Notes

- **FFmpeg** is required for format conversion and metadata embedding. The installer will attempt to set it up automatically.
- Downloaded files are saved in your system's Downloads folder under `Youtube Downloader MAA`.

## License

MIT License

```text
Copyright (c) 2025 Mosa Amran Alawadhi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

_For issues or contributions, please open an issue or pull request on GitHub._
