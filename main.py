from yt_dlp import YoutubeDL


def download(url: str, opt: dict[str, str]):
    with YoutubeDL(opt) as ydl:
        ydl.download([url])


if __name__ == '__main__':
    url = 'https://music.youtube.com/watch?v=8VLXHyHRXjc&si=1iUnT8lUPj17E80e'
    ydl_opt = {
        'format': 'bestvideo+bestaudio',
        'outtmpl': '%(title)s.%(ext)s'
    }
    download(url, ydl_opt)
