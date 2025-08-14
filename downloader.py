
import os
import subprocess
from typing import Tuple
import yt_dlp

def download_best_audio(url: str, out_dir: str) -> Tuple[str, str]:
    """Download best audio and convert to mp3 via yt_dlp/ffmpeg.
    Returns (mp3_path, title).
    """
    os.makedirs(out_dir, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(out_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'noplaylist': True,
        'quiet': False,
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'audio')
        # After post-processing, the file should be {title}.mp3 in out_dir
        mp3_path = os.path.join(out_dir, f"{title}.mp3")
        if not os.path.exists(mp3_path):
            # Sometimes yt-dlp sanitizes differently; find first mp3 in out_dir
            candidates = [f for f in os.listdir(out_dir) if f.lower().endswith('.mp3')]
            if candidates:
                mp3_path = os.path.join(out_dir, candidates[0])
            else:
                raise FileNotFoundError("MP3 not found after download.")
        return mp3_path, title
