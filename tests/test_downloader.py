

from yt_dlp import YoutubeDL
import os
from json.encoder import JSONEncoder

yt = YoutubeDL({'fmt': 'bestvideo+bestaudio'})
url = 'https://music.youtube.com/watch?v=sD0-b2cAQ2Q&si=c_Ef_8B4AbumKuWB'

with open(os.path.join(os.path.dirname(__file__), 'info.json'), 'w') as file:
    info = yt.extract_info(url=url, download=False)
    json_encoder = JSONEncoder()
    file.write(json_encoder.encode(info))
