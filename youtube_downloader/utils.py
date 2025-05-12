import winreg as reg
import re
import os
import platform
import requests
import zipfile
import tarfile
import shutil
import tempfile
from tkinter import filedialog, messagebox


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
    # base_path: str = os.path.join(os.path.dirname(__file__), 'bin', 'ffmpeg', 'ffmpeg-7.1-essentials_build', 'bin')
    base_path: str = os.path.join(os.path.dirname(__file__), 'bin', 'ffmpeg')
    ffmpeg_dir = None

    for entry in os.listdir(base_path):
        if os.path.isdir(os.path.join(base_path, entry)) and entry.startswith('ffmpeg-'):
            ffmpeg_dir = entry
            break

    if ffmpeg_dir:
        match = re.search(
            r'ffmpeg-(\d+\.\d+(?:\.\d+)?|latest)(?:-|$)', ffmpeg_dir)
        if not match:
            ffmpeg_dir = download_latest_ffmpeg(base_path)

        return os.path.join(ffmpeg_dir, 'bin')


def get_referenced_folder(folder_name: str):
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


def validate_url(url: str) -> bool:
    """Validates if the provided string is a proper YouTube URL."""
    youtube_url_pattern = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie|music\.youtube)\.(com|be)/.+"
    return bool(re.match(youtube_url_pattern, url))


def open_dir(path: str) -> int:
    return os.system(f'explorer /select,"{path}"') if platform.system() == "Windows" else os.system(
        f'nautilus "{path}"')


def select_dir(
        initial_dir: str | bytes | os.PathLike[str] | os.PathLike[bytes] | None = None,
        title: str | None = 'Select directory') -> str:
    return filedialog.askdirectory(initialdir=initial_dir, title=title)


def ask_select_dir(message: str, title: str = 'Select a directory?'):
    return messagebox.askyesno(title=title, message=message)


def ask_video_audio(
        message: str = "Video or Audio?\n"
                       'Yes = Video\n'
                       'No = Audio\n',
        title: str = 'Select a subtype'
) -> bool:
    """
    return True for Video, False for Audio
    """
    return messagebox.askyesno(title=title, message=message)


def show_title(title, subtype: str = 'video', text: str = '{} title:'):
    print(
        text.format(subtype.capitalize())
    )
    print(GREEN, title, RESET)


def exit_message():
    print(YELLOW, 'Thanks for using our YouTube Downloader.', RESET)
    print(CYAN, '\tMADE BY MAA\t'.center(50, "#"), RESET)
    # sleep(0.8)
    print(f'{RED}Exiting from downloader...{RESET}')
    # sleep(0.8)


def show_download_message(media_type='video', text=''):
    print(
        CYAN,
        f'Downloading the {media_type.capitalize()} {text}\n',
        'It may take a long time. Please wait...',
        RESET,
        sep=''
    )


def is_file_exist(path: str) -> bool:
    return os.path.exists(path)


if __name__ == '__main__':
    print(get_ffmpeg_path())
