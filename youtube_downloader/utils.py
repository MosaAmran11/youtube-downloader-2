import winreg as reg
import platform
import re
import os
from tkinter import filedialog, messagebox


RED: str = '\033[31m'
GREEN: str = '\033[32m'
YELLOW: str = '\033[33m'
BLUE: str = '\033[34m'
MAGENTA: str = '\033[35m'
CYAN: str = '\033[36m'
RESET: str = '\033[39m'
CLEAR: str = 'cls' if platform.system() == 'Windows' else 'clear'
BIN: str = os.path.join(os.path.dirname(__file__), 'bin', 'ffmpeg')


def get_referenced_folder(folder_name: str):
    registry_folder_names: [str, str] = {
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
            folder_path, regtype = reg.QueryValueEx(registry_key, registry_folder_names.get(folder_name))
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

print()
# print(ask_select_dir('Would you like to select a dir?'))
# u = 'https://music.youtube.com/watch?v=xrSayrw9Nvs&si=VUdLB3_xDVNA_Pzu'
# print(validate_url(u))
