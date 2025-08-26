from flask import Blueprint, render_template, request
from app.routes import download_service

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    """Main page route"""
    url = request.form.get('url') or ''
    video_info = None
    error = None

    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                video_info = download_service.get_video_info(url)
            except Exception as e:
                error = str(e)

    return render_template('index.html', url=url, video_info=video_info, error=error)
