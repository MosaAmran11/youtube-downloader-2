from youtube_downloader.yt_downloader import YoutubeDownloader


url = 'https://music.youtube.com/watch?v=xrSayrw9Nvs&si=Btb3ac-0jitm8t4r'
vid = YoutubeDownloader(url)
vid.download_video(resolution='720')
