# from yt_dlp import YoutubeDL
#
#
# def download(url: str, opt: dict[str, str]):
#     with YoutubeDL(opt) as ydl:
#         ydl.download([url])
#
#
# if __name__ == '__main__':
#     url = 'https://music.youtube.com/watch?v=8VLXHyHRXjc&si=1iUnT8lUPj17E80e'
#     ydl_opt = {
#         'format': 'bestvideo+bestaudio',
#         'outtmpl': '%(title)s.%(ext)s'
#     }
#     download(url, ydl_opt)

from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
from datetime import timedelta
import subprocess
import platform

app = Flask(__name__)

# Global variable to store progress
progress_hook = None


def format_duration(seconds):
    return str(timedelta(seconds=seconds))


def format_size(size_bytes):
    """Convert size in bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}GB"


def open_file_location(filepath):
    """Open file location in file explorer"""
    if platform.system() == "Windows":
        os.startfile(os.path.dirname(filepath))
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", os.path.dirname(filepath)])
    else:  # Linux
        subprocess.run(["xdg-open", os.path.dirname(filepath)])


def open_file(filepath):
    """Open file with default application"""
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", filepath])
    else:  # Linux
        subprocess.run(["xdg-open", filepath])


class ProgressHook:
    def __init__(self):
        self.progress = {
            'status': 'downloading',
            'percentage': '0%',
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'speed': 0,
            'filename': ''
        }

    def __call__(self, d):
        if d['status'] == 'downloading':
            self.progress['status'] = 'downloading'
            self.progress['percentage'] = d.get('_percent_str', '0%').strip()
            self.progress['downloaded_bytes'] = d.get('downloaded_bytes', 0)
            self.progress['total_bytes'] = d.get('total_bytes', 0)
            self.progress['speed'] = d.get('speed', 0)
            self.progress['filename'] = d.get('filename', '')
        elif d['status'] == 'finished':
            self.progress['status'] = 'finished'
            self.progress['filename'] = d.get('filename', '')


def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Get video formats
            formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    formats.append({
                        'format_id': f['format_id'],
                        'resolution': f.get('resolution', 'N/A'),
                        'ext': f.get('ext', 'N/A'),
                        'filesize': f.get('filesize', 0)
                    })

            # Get audio formats
            audio_formats = []
            for f in info.get('formats', []):
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    audio_formats.append({
                        'format_id': f['format_id'],
                        'abr': f.get('abr', 0),
                        'ext': f.get('ext', 'N/A'),
                        'filesize': f.get('filesize', 0)
                    })

            return {
                'title': info.get('title', 'Unknown Title'),
                'duration': format_duration(info.get('duration', 0)),
                'url': url,
                'formats': formats,
                'audio_formats': audio_formats
            }
    except Exception as e:
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    error = None

    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            video_info = get_video_info(url)
            if not video_info:
                error = "Could not fetch video information. Please check the URL and try again."

    return render_template('index.html', video_info=video_info, error=error)


@app.route('/download', methods=['POST'])
def download():
    global progress_hook
    url = request.form.get('url')
    format_id = request.form.get('format')
    audio_format_id = request.form.get('audio_format')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    progress_hook = ProgressHook()
    ydl_opts = {
        'format': format_id if format_id else audio_format_id,
        'outtmpl': '%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
        'merge_output_format': 'mp4' if format_id else 'mp3',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # Remove the temporary file if it exists
            if os.path.exists(filename + '.part'):
                os.remove(filename + '.part')

            if os.path.exists(filename):
                return jsonify({
                    'status': 'success',
                    'filename': filename,
                    'filesize': os.path.getsize(filename)
                })
            else:
                return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/progress')
def get_progress():
    global progress_hook
    if progress_hook:
        return jsonify(progress_hook.progress)
    return jsonify({'status': 'not_started'})


@app.route('/open_location/<path:filename>')
def open_location(filename):
    try:
        open_file_location(filename)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/open_file/<path:filename>')
def open_file_route(filename):
    try:
        open_file(filename)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
