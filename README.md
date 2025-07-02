# YouTube Downloader

A modern, cross-platform YouTube video/audio downloader with a beautiful web-based GUI, built with Flask and yt-dlp.

## ⚠️ Disclaimer

This tool is intended for personal and educational use only.
Downloading copyrighted content without permission is against [YouTube's Terms of Service](https://www.youtube.com/static?template=terms).
The author is not responsible for any misuse of this tool.

## ✨ Features

- **Modern Web Interface**: Clean, responsive design with Bootstrap 5 and modular components
- **Multiple Format Support**: Download videos and audio in various qualities
- **Real-time Progress**: Live download progress with speed and size information
- **Smart Thumbnail Display**: Responsive thumbnails that adapt to aspect ratios
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Automatic FFmpeg Setup**: Downloads and configures FFmpeg automatically
- **File Management**: Open downloaded files or their locations directly from the UI
- **Modular Architecture**: Clean, maintainable code structure
- **Interactive Notifications**: Toast messages and snackbar notifications
- **Keyboard Shortcuts**: Quick access to common functions
- **Status Indicators**: Real-time system status and connection monitoring

## 🏗️ Project Structure

```
youtube_downloader/
├── app/                          # Flask application
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuration settings
│   ├── routes/                  # Route handlers
│   │   ├── main.py             # Main page routes
│   │   └── api.py              # API endpoints
│   ├── services/               # Business logic
│   │   ├── download_service.py # Download management
│   │   └── file_service.py     # File operations
│   └── utils/                  # Application utilities
│       ├── formatters.py       # Data formatting
│       └── validators.py       # Input validation
├── core/                       # Core functionality
│   ├── downloaders/           # Downloader implementations
│   │   ├── base.py           # Abstract base class
│   │   ├── youtube.py        # YouTube downloader
│   │   └── progress.py       # Progress tracking
│   └── utils/                # Core utilities
│       ├── file_utils.py     # File operations
│       ├── ffmpeg_utils.py   # FFmpeg management
│       └── platform_utils.py # Platform-specific code
├── static/                    # Static assets
│   ├── css/                  # Stylesheets
│   └── js/                   # JavaScript files
├── templates/                 # HTML templates
├── tests/                    # Test suite
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/youtube-downloader.git
   cd youtube-downloader
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - **Windows:**
     ```cmd
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Install FFmpeg (Optional - will be done automatically):**

   ```bash
   python scripts/install_ffmpeg.py
   ```

6. **Run the application:**

   ```bash
   python main.py
   ```

7. **Open your browser and go to:** [http://localhost:5000](http://localhost:5000)

### FFmpeg Installation

The application will automatically download and install FFmpeg if it's not found on your system. FFmpeg will be installed to:

- **Windows**: `C:\Program Files\FFmpeg\`
- **macOS**: `~/bin/`
- **Linux**: `~/bin/`

The installation process will:

1. Download the appropriate FFmpeg build for your platform
2. Install it to the system directory
3. Add it to your PATH environment variable
4. Verify the installation

**Note**: On Unix systems (macOS/Linux), you may need to restart your terminal or run `source ~/.bashrc` for the PATH changes to take effect.

### Manual FFmpeg Installation

If automatic installation fails, you can install FFmpeg manually:

- **Windows**: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

## 📖 Usage

1. **Enter a YouTube URL** in the input field
2. **Click "Get Info"** to fetch video information
3. **Select your preferred format** from the available options
4. **Click "Download"** to start the download
5. **Monitor progress** in real-time
6. **Open the file** or its location when complete

## 🎨 Web Interface Features

### **Modular Components**

- **Title Bar**: Navigation, branding, and status indicators
- **Snackbar Notifications**: Toast messages for user feedback
- **Video Cards**: Responsive display of video information
- **Download Forms**: Format selection and download controls
- **Progress Tracking**: Real-time download progress with speed and size
- **File Actions**: Open files or their locations after download

### **Interactive Features**

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Smart Thumbnails**: Automatically adjusts size based on aspect ratio
- **Keyboard Shortcuts**: Quick access to common functions
- **Status Indicators**: Real-time system and connection status
- **Loading States**: Visual feedback during operations
- **Error Handling**: Graceful error messages and recovery

### **User Experience**

- **Modern UI**: Clean, professional design with smooth animations
- **Accessibility**: Keyboard navigation and screen reader support
- **Performance**: Optimized loading and smooth interactions
- **Cross-browser**: Works on Chrome, Firefox, Safari, and Edge

## 🔧 Configuration

The application can be configured through environment variables:

- `FLASK_DEBUG`: Set to `True` for development mode (default: `True`)
- `FLASK_HOST`: Server host (default: `127.0.0.1`)
