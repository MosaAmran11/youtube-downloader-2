#!/usr/bin/env python3
"""
FFmpeg Installation Script
Standalone script to download and install FFmpeg system-wide
"""
from downloaders.utils.ffmpeg_utils import (
    ensure_ffmpeg_available,
    verify_ffmpeg_installation,
    get_ffmpeg_install_dir
)
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    """Main installation function"""
    print("🎬 FFmpeg Installation Script")
    print("=" * 40)

    # Show installation directory
    install_dir = get_ffmpeg_install_dir()
    print(f"Installation directory: {install_dir}")

    # Check if FFmpeg is already available
    print("\n🔍 Checking current FFmpeg installation...")
    if verify_ffmpeg_installation():
        print("✅ FFmpeg is already installed and working!")
        return

    # Install FFmpeg
    print("\n📥 Installing FFmpeg...")
    if ensure_ffmpeg_available():
        print("\n✅ FFmpeg installation completed successfully!")

        # Verify installation
        print("\n🔍 Verifying installation...")
        if verify_ffmpeg_installation():
            print("✅ FFmpeg is working correctly!")
            print("\n🎉 Installation complete! You can now use FFmpeg from anywhere.")
        else:
            print("⚠️  Installation completed but verification failed.")
            print("Please restart your terminal and try again.")
    else:
        print("❌ FFmpeg installation failed!")
        print("Please check your internet connection and try again.")


if __name__ == '__main__':
    main()
