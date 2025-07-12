import os
import requests

from PIL import Image
from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3

from downloaders.utils.file_utils import get_downloader_paths as paths
from downloaders.utils.file_utils import safe_name
from downloaders.utils import raise_on_error


@raise_on_error()
def embed_thumbnail(audio_filename: str, thumbnail_path: str):
    if not audio_filename or not thumbnail_path:
        raise ValueError("Audio filename and thumbnail path must be provided")

    print(f'[Thumbnail] Adding thumbnail to "{audio_filename}"')

    # Ensure thumbnail is JPEG
    jpeg_thumb_path = thumbnail_path
    try:
        with Image.open(thumbnail_path) as img:
            if img.format != 'JPEG':
                jpeg_thumb_path = thumbnail_path.rsplit('.', 1)[0] + '.jpg'
                img.convert('RGB').save(jpeg_thumb_path, 'JPEG')
    except:
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


@raise_on_error()
def download_thumbnail(url: str, title: str = 'thumbnail') -> str:
    """Download the best thumbnail for album cover.
    :return: The path to the downloaded thumbnail."""
    if not url:
        raise ValueError("No thumbnail URL provided")

    path = os.path.join(paths().get('thumbnail'),
                        f'{safe_name(title)}_thumbnail.png')
    os.makedirs(paths().get('thumbnail'), exist_ok=True)

    print("Downloading thumbnail...")

    thumbnail_data = requests.get(url).content
    with open(path, 'wb') as f:
        f.write(thumbnail_data)

    print(f"Downloaded thumbnail: {path} ({len(thumbnail_data)} bytes)")
    return path
