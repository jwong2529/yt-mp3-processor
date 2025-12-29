import os
import subprocess

def download_temp_video(video_url: str, tmp_dir: str) -> str:
    """Download the YouTube video as a temp MP4 for ffmpeg frame extraction."""
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, "temp_video.%(ext)s")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": tmp_path,
        "merge_output_format": "mp4",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        return ydl.prepare_filename(info)  # Returns the actual downloaded file path

def extract_frame_from_file(video_path: str, timestamp_sec: float, out_path: str) -> str:
    """Extract a frame from a local video file."""
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp_sec),
        "-i", video_path,
        "-frames:v", "1",
        out_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out_path

def extract_frame_to_jpeg(video_url: str, timestamp_sec: float, out_path: str, tmp_dir: str = "tmp") -> str:
    """Download video then extract frame (works with YouTube)."""
    local_video = download_temp_video(video_url, tmp_dir)
    return extract_frame_from_file(local_video, timestamp_sec, out_path)

import cv2
import yt_dlp

def pick_frame_interactive(video_url: str, tmp_dir: str) -> str:
    """Interactive video scrubber to pick cover frame."""
    video_path = download_temp_video(video_url, tmp_dir)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError("Failed to open video.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_idx = 0

    print("Use arrow keys to scrub, [SPACE] to save frame, [Q] to quit.")

    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break

        display_frame = frame.copy()
        cv2.putText(display_frame, f"{frame_idx/fps:.2f} s", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Arrow keys to scrub -- [SPACE] to save -- [Q] to quit", display_frame)

        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            break
        elif key in [81, 2, 2424832]:  # Left arrow
            frame_idx = max(frame_idx - int(fps), 0)
        elif key in [83, 3, 2555904]:  # Right arrow
            frame_idx = min(frame_idx + int(fps), total_frames - 1)
        elif key == 32:  # Space to save
            out_path = os.path.join(tmp_dir, "cover.jpg")
            cv2.imwrite(out_path, frame)
            print(f"Frame saved to {out_path}")
            cap.release()
            cv2.destroyAllWindows()
            return out_path

    cap.release()
    cv2.destroyAllWindows()
    return ""
