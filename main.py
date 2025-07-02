#!/usr/bin/env python3
"""
YouTube Downloader - Main Entry Point
A cross-platform YouTube video/audio downloader with web interface
"""

import os
import sys
import socket
from app import create_app
from downloaders.utils.file_utils import ensure_directories_exist
from downloaders.utils.ffmpeg_utils import ensure_ffmpeg_available, verify_ffmpeg_installation


def find_available_port(start_port: int = 5000, max_attempts: int = 10) -> int | None:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None


def main():
    """Main application entry point"""
    print("Starting YouTube Downloader...")

    # Ensure required directories exist
    ensure_directories_exist()

    # Check and setup FFmpeg
    print("Checking FFmpeg availability...")
    if not ensure_ffmpeg_available():
        print("Warning: FFmpeg setup failed. Some features may not work properly.")
        print("You can manually install FFmpeg and add it to your PATH.")
    else:
        # Verify the installation
        if verify_ffmpeg_installation():
            print("✅ FFmpeg is ready to use!")
        else:
            print(
                "⚠️  FFmpeg installed but verification failed. You may need to restart your terminal.")

    # Create and run Flask app
    app = create_app()

    # Get configuration
    debug = app.config.get('DEBUG', True)
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    preferred_port = int(os.environ.get('FLASK_PORT', 5000))

    # Find available port
    port = find_available_port(preferred_port)
    if port is None:
        print(
            f"❌ No available ports found in range {preferred_port}-{preferred_port + 9}")
        print("Please close other applications or specify a different port with FLASK_PORT environment variable")
        sys.exit(1)

    # if port != preferred_port:
    #     print(
    #         f"⚠️  Port {preferred_port} is in use, using port {port} instead")

    # print(f"\n🚀 Server starting on http://{host}:{port}")
    # print("Press Ctrl+C to stop the server")

    try:
        app.run(host=host, port=port, debug=debug)
    except OSError as e:
        if "permission" in str(e).lower() or "access" in str(e).lower():
            print(f"❌ Permission error: {e}")
            print("Try running with administrator privileges or use a different port")
            print(
                "You can set a different port with: set FLASK_PORT=8080 && python main.py")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
