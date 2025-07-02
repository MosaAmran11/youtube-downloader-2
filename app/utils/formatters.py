from datetime import timedelta
import re


def format_duration(seconds: int | float | str) -> str:
    """Format duration in seconds to HH:MM:SS format"""
    if isinstance(seconds, str):
        return seconds

    duration = timedelta(seconds=float(seconds))
    formatted = str(duration)

    # Remove leading zero from hours if present
    formatted = re.sub(r'^0:', '', formatted)

    # Ensure all parts have at least 2 digits
    parts = formatted.split(':')
    formatted_parts = [part.zfill(2) for part in parts]

    return ':'.join(formatted_parts)


def format_size(size_bytes: float) -> str:
    """Convert size in bytes to human-readable format"""
    if not size_bytes:
        return ''

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.1f}GB"


def format_speed(bytes_per_second: float) -> str:
    """Format download speed"""
    return f"{format_size(bytes_per_second)}/s"
