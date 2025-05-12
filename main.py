from flask import Flask, render_template, request, send_file, jsonify
import os
from datetime import timedelta
import subprocess
import platform
from youtube_downloader.downloader import Downloader

app = Flask(__name__)

# Global variable to store downloader instance
current_downloader = None


def format_duration(seconds):
    return str(timedelta(seconds=seconds))


def format_size(size_bytes):
    """Convert size in bytes to human-readable fmt"""
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


# class ProgressHook:
#     def __init__(self):
#         self.progress = {
#             'status': 'downloading',
#             'percentage': '0%',
#             'downloaded_bytes': 0,
#             'total_bytes': 0,
#             'speed': 0,
#             'filename': ''
#         }
#
#     def __call__(self, d):
#         if d['status'] == 'downloading':
#             self.progress['status'] = 'downloading'
#             self.progress['percentage'] = d.get('_percent_str', '0%').strip()
#             self.progress['downloaded_bytes'] = d.get('downloaded_bytes', 0)
#             self.progress['total_bytes'] = d.get('total_bytes', 0)
#             self.progress['speed'] = d.get('speed', 0)
#             self.progress['filename'] = d.get('filename', '')
#         elif d['status'] == 'finished':
#             self.progress['status'] = 'finished'
#             self.progress['filename'] = d.get('filename', '')


@app.route('/', methods=['GET', 'POST'])
def index():
    global current_downloader
    video_info = None
    error = None

    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                current_downloader = Downloader(url)
                video_info = current_downloader.get_video_info()
            except Exception as e:
                error = f"Could not fetch video information. Please check the URL and try again. {e}"

    return render_template('index.html', video_info=video_info, error=error)


@app.route('/download', methods=['POST'])
def download():
    global current_downloader
    if not current_downloader:
        return jsonify({'error': 'No video selected'}), 400

    format_id = request.form.get('fmt')
    audio_format_id = request.form.get('audio_format')

    try:
        # Get the fmt object from the available formats
        if format_id:
            format_obj = next((f for f in current_downloader.get_video_formats()
                               if f['format_id'] == format_id), None)
        else:
            format_obj = next((f for f in current_downloader.get_audio_formats()
                               if f['format_id'] == audio_format_id), None)

        if not format_obj:
            return jsonify({'error': 'Selected fmt not found'}), 400

        # Download the file
        file_path = current_downloader.download(format_obj)

        if os.path.exists(file_path):
            return jsonify({
                'status': 'success',
                'filename': file_path,
                'filesize': os.path.getsize(file_path),
                'type': 'video' if format_id else 'audio'
            })
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/progress')
def get_progress():
    if current_downloader and hasattr(current_downloader, 'progress_hook'):
        return jsonify(current_downloader.progress_hook.progress)
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
