from flask import Flask, render_template, request, send_file, jsonify
import os
from datetime import timedelta
import subprocess
import platform
from downloaders.downloader import Downloader
import threading

app = Flask(__name__)

# Global variable to store downloader instance
# Downloader instance with empty URL. (Instead of `None` to avoid NoneType errors)
current_downloader = Downloader('')
thread = None


def format_duration(seconds):
    return str(timedelta(seconds=seconds))


def format_size(size_bytes):
    """Convert size in bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}GB"


def open_file_location(filepath):
    """Open file location in file explorer"""
    if platform.system() == "Windows":
        os.system(f'explorer /select,"{os.path.normpath(filepath)}"')
    elif platform.system() == "Darwin":  # macOS
        os.system(f'open "{os.path.dirname(filepath)}"')
    else:  # Linux
        os.system(f'xdg-open "{os.path.dirname(filepath)}"')


def open_file(filepath):
    """Open file with default application"""
    if platform.system() == "Windows":
        os.startfile(filepath)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", filepath])
    else:  # Linux
        subprocess.run(["xdg-open", filepath])


@app.route('/', methods=['GET', 'POST'])
def index():
    global current_downloader
    url = request.form.get('url') or ''
    video_info = None
    error = None

    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                current_downloader = Downloader(url)
                video_info = current_downloader.get_video_info()
            except Exception as e:
                error = "Could not fetch video information. Please check the URL and try again."

    return render_template('index.html', url=url, video_info=video_info, error=error)


@app.route('/download', methods=['POST'])
def download():
    global current_downloader
    if not current_downloader.url:
        return jsonify({'error': 'No video selected'}), 400

    format_id = request.form.get('format')
    format_obj = None

    try:
        # Get the format object from the available formats
        if format_id:
            format_obj = next((f for f in current_downloader.info.get('formats', [])
                               if f['format_id'] == format_id), None)
        if not format_obj:
            return jsonify({'error': 'Selected format not found'}), 400

        # Start download in a background thread
        def download_thread():
            try:
                file_path = current_downloader.download(format_obj)
                if os.path.exists(file_path):
                    current_downloader.progress_hook.progress['status'] = 'finished'
                    current_downloader.progress_hook.progress['filename'] = file_path
                else:
                    current_downloader.progress_hook.progress['status'] = 'error'
                    current_downloader.progress_hook.progress['error'] = 'File not found'
            except Exception as e:
                current_downloader.progress_hook.progress['status'] = 'error'
                current_downloader.progress_hook.progress['error'] = str(e)

        # Reset progress
        current_downloader.progress_hook.progress = {
            'status': 'downloading',
            'percentage': '0%',
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'speed': 0,
            'filename': ''
        }

        # Start the download thread
        global thread
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()

        return jsonify({'status': 'started'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/progress')
def get_progress():
    if current_downloader and hasattr(current_downloader, 'progress_hook'):
        if thread and thread.is_alive():
            current_downloader.progress_hook.progress['status'] = 'downloading'
        return jsonify(current_downloader.progress_hook.progress)
    return jsonify({'status': 'not_started'})


@app.route('/open_location/<path:filename>')
def open_location(filename):
    try:
        # Convert URL-encoded path to absolute path
        abs_path = os.path.abspath(filename)
        open_file_location(abs_path)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/open_file/<path:filename>')
def open_file_route(filename):
    try:
        # Convert URL-encoded path to absolute path
        abs_path = os.path.abspath(filename)
        open_file(abs_path)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
