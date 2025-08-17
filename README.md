
# YouTube → MP3 with Search, Metadata, Cover Art, and Trimming

A fully interactive Python tool that lets you:
- Search YouTube by **URL or keywords** (pick from results in terminal)
- Download **audio as MP3**
- **Trim** audio (manual times or interactive waveform GUI)
- **Edit/clear metadata** (CLI or a small **Tkinter GUI**)
- Set **cover art** from a video frame (FFmpeg), pick a local image, or use a frame scrubber
- **Rename** and save to a target folder read from `.env`

Use case:
Provides a more streamlined process for importing Youtube audio to Spotify local files.

## Quick Start (macOS / Linux)
1. **Install FFmpeg** (required by `yt_dlp`/`pydub` for conversions and frame extraction)
   - macOS (Homebrew): `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y ffmpeg`

2. **Create and activate a virtualenv (recommended)**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your save directory in `.env`**
   - Copy `.env.sample` → `.env`, then set `SAVE_DIR` to your iCloud Drive folder, e.g.:
     ```env
     SAVE_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Music/YouTubeMP3"
     ```
   - Create that folder if it doesn't exist.

5. **Run**
    
    For full process, starting with downloading YouTube video:
   ```bash
   python main.py
   ```
   
    For editing metadata and cover art of existing .mp3 file:
    ```bash
   python edit_existing.py
    ```

## Features & Flow
- **Search**: Enter a YouTube URL _or_ keywords; for keywords it shows a selectable list (title, channel, duration).
- **Download**: Best audio stream, converts to `.mp3` with `yt_dlp` + FFmpeg.
- **Trim (optional)**:
  - Manual: enter start/end in seconds (e.g., `5.5` to `182.3`).
  - Interactive: pop-up waveform window; press [SPACE] and arrow keys to select start/end times and close the window to apply.
- **Metadata**:
  - CLI mode: prompts for Title/Artist/Album/etc., or choose to clear all.
  - GUI mode: Tkinter form; save to apply.
- **Cover Art**:
  - From frame: enter timestamp (e.g., `45.2`) and we grab a frame with FFmpeg.
  - From file: choose an image.
  - From scrubber: use arrow keys to scrub through and choose a frame
- **Rename**: Final prompt to rename the file before saving.
- **Save**: Writes to `SAVE_DIR` from `.env`. 

## Notes
- If you get an FFmpeg-related error, confirm `ffmpeg` is installed and on your PATH.
- On first run, some packages may take a moment to build wheels.
- After picking times in the interactive waveform, close the window to continue to further instructions.
- If the youtube video fails to download, update `yt-dlp`.
```bash
   pip install -U yt-dlp
```
If it still doesn't work, the format is not supported. Download the video with [Y2mate](https://v4.www-y2mate.com/).
Place the file in your iCloud folder and then run  
```bash
   python edit_existing.py
```
to edit metadata and select cover art.

## Uninstall / Clean
- Remove the `.venv` folder to drop the environment.