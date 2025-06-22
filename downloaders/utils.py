import re
import os
import platform
from typing import TextIO
import requests
import zipfile
import tarfile
import shutil
import tempfile
from PIL import Image
from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3

RED: str = '\033[31m'
GREEN: str = '\033[32m'
YELLOW: str = '\033[33m'
BLUE: str = '\033[34m'
MAGENTA: str = '\033[35m'
CYAN: str = '\033[36m'
RESET: str = '\033[39m'
CLEAR: str = 'cls' if platform.system() == 'Windows' else 'clear'


def download_latest_ffmpeg(base_path: str):
    system = platform.system()
    arch = platform.machine()

    print(f"Detected platform: {system} {arch}")

    if system == "Windows":
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        archive_ext = ".zip"
    elif system == "Linux":
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        archive_ext = ".tar.xz"
    elif system == "Darwin":  # macOS
        url = "https://evermeet.cx/ffmpeg/getrelease/zip"
        archive_ext = ".zip"
    else:
        print("Unsupported operating system.")
        return

    print("Downloading FFmpeg from:", url)
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print("Failed to download FFmpeg.")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=archive_ext) as tmp_file:
        for chunk in response.iter_content(chunk_size=8192):
            tmp_file.write(chunk)
        archive_path = tmp_file.name

    temp_extract_path = tempfile.mkdtemp()

    try:
        print("Extracting archive...")
        if archive_ext == ".zip":
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_path)
        elif archive_ext == ".tar.xz":
            with tarfile.open(archive_path, "r:xz") as tar_ref:
                tar_ref.extractall(temp_extract_path)

        # Find directory or binaries inside the extracted content
        extracted_dir = next(os.walk(temp_extract_path))[0]
        contents = os.listdir(extracted_dir)

        # Determine version and structure
        version = None
        ffmpeg_bin_path = None
        for item in contents:
            if re.search(r'ffmpeg-(\d+\.\d+(?:\.\d+)?|latest)(?:-|$)', item):
                version = re.search(
                    r'ffmpeg-(\d+\.\d+(?:\.\d+)?|latest)(?:-|$)', item).group(1)
                ffmpeg_bin_path = os.path.join(extracted_dir, item)
                break
            if item == "ffmpeg" or item == "ffmpeg.exe":
                version = "latest"
                ffmpeg_bin_path = extracted_dir
                break

        if not ffmpeg_bin_path:
            print("Could not determine FFmpeg binary directory.")
            return

        # Target output directory
        target_dir = os.path.join(
            base_path, f"ffmpeg-{version}-essentials_build")
        os.makedirs(base_path, exist_ok=True)
        if os.path.exists(target_dir):
            print(f"FFmpeg {version} already exists.")
        else:
            shutil.move(ffmpeg_bin_path, target_dir)
            print(f"FFmpeg {version} installed at {target_dir}")
        return target_dir

    finally:
        os.remove(archive_path)
        shutil.rmtree(temp_extract_path)


def get_ffmpeg_path():
    if platform.system() == 'Linux':
        # Check if ffmpeg is installed and in PATH
        if shutil.which('ffmpeg'):
            return shutil.which('ffmpeg')

    base_path: str = os.path.join(os.path.dirname(__file__), 'bin', 'ffmpeg')
    ffmpeg_dir = None

    if os.path.exists(base_path):
        for entry in os.listdir(base_path):
            if os.path.isdir(os.path.join(base_path, entry)) and entry.startswith('ffmpeg-'):
                ffmpeg_dir = entry
                break

    if ffmpeg_dir:
        match = re.search(
            r'ffmpeg-(\d+\.\d+(?:\.\d+)?|latest)(?:-|$)', ffmpeg_dir)
        if not match:
            ffmpeg_dir = download_latest_ffmpeg(base_path)

        for i in os.listdir(os.path.join(base_path, ffmpeg_dir, 'bin')):
            if i.startswith('ffmpeg'):
                pth = os.path.normpath(os.path.join(
                    base_path, ffmpeg_dir, 'bin', i))
                return pth
    return None


def get_referenced_folder(folder_name: str):
    if platform.system() != 'Windows':
        return None
    import winreg as reg
    registry_folder_names: dict[str, str] = {
        'Downloads': '{374DE290-123F-4565-9164-39C4925E467B}',
        'Saved Games': '{4C5C32FF-BB9D-43B0-B5B4-2D72E54EAAA4}',
        'Contacts': '{56784854-C6CB-462B-8169-88E350ACB882}',
        'Searches': '{7D1D3A04-DEBB-4115-95CF-2F29DA2920DA}',
        'Documents': 'Personal',
        'Music': 'My Music',
        'Pictures': 'My Pictures',
        'Videos': 'My Video'
    }
    try:
        # Open the registry key for the current user
        with reg.OpenKey(reg.HKEY_CURRENT_USER,
                         r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as registry_key:
            # Read the value for the Downloads folder
            folder_path, regtype = reg.QueryValueEx(
                registry_key, registry_folder_names.get(folder_name))
            return folder_path
    except FileNotFoundError:
        original_folder_name: str = next(
            (key for key, val in registry_folder_names.items() if val == folder_name), None)
        print(f"{original_folder_name} folder entry not found in the registry.")
        return None


def safe_name(name: str) -> str:
    """
    Sanitize a string to be safe for use as a file name on most file systems.
    Removes or replaces characters not allowed in Windows, macOS, and Linux file names.
    """
    # Remove or replace forbidden characters: \ / : * ? " < > | and control chars
    name = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', name)
    # Remove non-printable/control characters
    name = ''.join(c for c in name if c.isprintable() and ord(c) > 31)
    # Optionally, strip leading/trailing whitespace and dots (not allowed on Windows)
    name = name.strip().strip('.')
    # Limit length (most filesystems support 255 bytes for a filename)
    return name[:250]  # The rest 5 characters are reserved for file extension


def prepare_filename(info: dict, dir_type: str, outtmpl: str) -> str:
    """
    Prepare a filename based on the video information and output template.
    :param dir_type:
    :param info: A dictionary containing video information.
    :param outtmpl: The output template for the filename.
    :return: An absolute path with formatted filename string.
    """
    filename = safe_name(outtmpl % info)
    file_path = os.path.join(paths().get(dir_type), filename)
    return file_path


def paths() -> dict[str, str]:
    """Returns a dictionary of paths for various directories."""
    app_name: str = "Youtube Downloader MAA"
    if platform.system() == 'Windows':
        base_path = os.path.join(
            get_referenced_folder('Downloads'),
            app_name)
    else:
        base_path = os.path.join(
            os.getenv("HOME"),
            'Downloads',
            app_name)
    return {
        'home': base_path,
        'video': os.path.join(base_path, 'Video'),  # Directory for video files
        'audio': os.path.join(base_path, 'Audio'),  # Directory for audio files
        # Directory for subtitle files
        'subtitle': os.path.join(base_path, 'Subtitles'),
        # Temporary download path for fragmented files
        'temp': os.path.join(base_path, '.temp'),
        # Directory for thumbnail images
        'thumbnail': os.path.join(base_path, '.thumbnails'),
    }


def embed_thumbnail(audio_filename: str, thumbnail_path: str):
    print("Embedding thumbnail into audio file...")

    # Ensure thumbnail is JPEG
    jpeg_thumb_path = thumbnail_path
    try:
        with Image.open(thumbnail_path) as img:
            if img.format != 'JPEG':
                jpeg_thumb_path = thumbnail_path.rsplit('.', 1)[0] + '.jpg'
                img.convert('RGB').save(jpeg_thumb_path, 'JPEG')
    except Exception as e:
        jpeg_thumb_path = thumbnail_path  # fallback

    # Embed the thumbnail image into the audio file
    try:
        audio = MP3(audio_filename, ID3=ID3)
        audio.tags.add(APIC(
            encoding=3,  # 3 = utf-8
            mime='image/jpeg',  # MIME type of the image
            type=3,  # 3 = cover image
            desc='Cover',
            data=open(jpeg_thumb_path, 'rb').read()
        ))
        audio.save(v2_version=3)
    except error:
        # If the file has no existing ID3 tags, add them
        audio = MP3(audio_filename)
        audio.add_tags()
        audio.tags.add(APIC(
            encoding=3,
            mime='image/jpeg',
            type=3,
            desc='Cover',
            data=open(jpeg_thumb_path, 'rb').read()
        ))
        audio.save(v2_version=3)

    # Clean up the downloaded thumbnail image
    os.remove(thumbnail_path)


def download_thumbnail(url: str, title: str = 'thumbnail') -> str:
    """Download the best thumbnail for album cover.
    :param info: A dictionary containing video information, including the thumbnail URL and title.
    :param path: The path where the thumbnail will be saved.
    :return: The path to the downloaded thumbnail."""
    path = os.path.join(paths().get('thumbnail'),
                        f'{safe_name(title)}_thumbnail.png')
    os.makedirs(paths().get('thumbnail'), exist_ok=True)

    print("Downloading thumbnail...")

    thumbnail_data = requests.get(url).content
    with open(path, 'wb') as f:
        f.write(thumbnail_data)

    print(f"Downloaded thumbnail: {path} ({len(thumbnail_data)} bytes)")
    return path


def validate_url(url: str) -> bool:
    """Validates if the provided string is a proper YouTube URL."""
    youtube_url_pattern = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie|music\.youtube)\.(com|be)/.+"
    return bool(re.match(youtube_url_pattern, url))
