import re
from urllib.parse import urlparse


def is_valid_youtube_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube URL"""
    if not url:
        return False

    # Parse the URL
    parsed = urlparse(url)

    # Check if it's a valid URL
    if not parsed.scheme or not parsed.netloc:
        return False

    # YouTube domain patterns
    youtube_domains = [
        'youtube.com',
        'www.youtube.com',
        'm.youtube.com',
        'youtu.be',
        'music.youtube.com'
    ]

    # Check if domain is YouTube
    if parsed.netloc not in youtube_domains:
        return False

    # Check for video ID patterns
    video_patterns = [
        r'/watch\?v=([a-zA-Z0-9_-]{11})',
        r'/embed/([a-zA-Z0-9_-]{11})',
        r'/v/([a-zA-Z0-9_-]{11})',
        r'/youtu\.be/([a-zA-Z0-9_-]{11})'
    ]

    for pattern in video_patterns:
        if re.search(pattern, url):
            return True

    return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    # Remove or replace forbidden characters
    filename = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', filename)

    # Remove non-printable characters
    filename = ''.join(c for c in filename if c.isprintable() and ord(c) > 31)

    # Strip leading/trailing whitespace and dots
    filename = filename.strip().strip('.')

    # Limit length
    return filename[:250]
