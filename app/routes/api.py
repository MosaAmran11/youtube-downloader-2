from flask import Blueprint, request, jsonify
from app.services.download_service import DownloadService
from app.services.file_service import FileService

api_bp = Blueprint('api', __name__)
download_service = DownloadService()
file_service = FileService()


@api_bp.route('/download', methods=['POST'])
def download():
    """Start a download"""
    try:
        url = request.form.get('url')
        format_id = request.form.get('format')
        if not url:
            return jsonify({'error': 'No video selected'})
        if not format_id:
            return jsonify({'error': 'No format selected'}), 400

        result = download_service.start_download(url, format_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/progress')
def get_progress():
    """Get download progress"""
    try:
        progress = download_service.get_progress()
        return jsonify(progress)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/open_location/<path:filename>')
def open_location(filename):
    """Open file location"""
    try:
        result = file_service.open_file_location(filename)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/open_file/<path:filename>')
def open_file(filename):
    """Open file with default application"""
    try:
        result = file_service.open_file(filename)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
