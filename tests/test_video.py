from youtube_downloader.video import Video


url = 'https://music.youtube.com/watch?v=xrSayrw9Nvs&si=Btb3ac-0jitm8t4r'
vid = Video(url)
vid.download()
