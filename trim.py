
from typing import Optional, Tuple
import os
import librosa
import numpy as np
import cv2
from pydub import AudioSegment

def format_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def trim_manual(mp3_path: str, start: Optional[float], end: Optional[float]) -> str:
    if start is None and end is None:
        return mp3_path
    audio = AudioSegment.from_file(mp3_path)
    ms_start = int((start or 0) * 1000)
    ms_end = int((end or (len(audio)/1000)) * 1000)
    ms_start = max(ms_start, 0)
    ms_end = min(ms_end, len(audio))
    if ms_end <= ms_start:
        raise ValueError("End must be greater than start.")
    trimmed = audio[ms_start:ms_end]
    out_path = append_suffix(mp3_path, "trim" )
    trimmed.export(out_path, format="mp3", bitrate="320k")
    return out_path

def append_suffix(path: str, suffix: str) -> str:
    base, ext = os.path.splitext(path)
    return f"{base}__{suffix}{ext}"

def trim_interactive(mp3_path: str) -> str:
    """Interactive audio scrub: SPACE to set start, SPACE to set end, Q to quit."""
    print("Loading audio...")
    y, sr = librosa.load(mp3_path, sr=None, mono=True)

    start_time = None
    end_time = None
    pos = 0  # current playback position in samples

    waveform_img = render_waveform(y, sr)
    print("Controls: SPACE to set start/end, ←/→ to scrub 1 sec, Q to quit.")

    while True:
        # copy waveform image to draw on
        img = waveform_img.copy()

        # Draw position line
        x_pos = int((pos / len(y)) * img.shape[1])
        cv2.line(img, (x_pos, 0), (x_pos, img.shape[0]), (0, 0, 255), 1)

        # Draw start/end markers
        if start_time is not None:
            s_x = int((start_time * sr / len(y)) * img.shape[1])
            cv2.line(img, (s_x, 0), (s_x, img.shape[0]), (0, 255, 0), 1)
        if end_time is not None:
            e_x = int((end_time * sr / len(y)) * img.shape[1])
            cv2.line(img, (e_x, 0), (e_x, img.shape[0]), (255, 0, 0), 1)

        # Show current time in seconds at top-left
        current_time_sec = pos / sr
        cv2.putText(
            img,
            f"Time: {format_time(current_time_sec)} s",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 0),
            2
        )

        cv2.imshow("Trim Audio", img)

        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            break
        elif key in [81, 2, 2424832]:  # left arrow
            pos = max(pos - sr, 0)
        elif key in [83, 3, 2555904]:  # right arrow
            pos = min(pos + sr, len(y) - 1)
        elif key == 32:  # SPACE
            current_time = pos / sr
            if start_time is None:
                start_time = current_time
                print(f"Start set at {format_time(start_time)} s")
            elif end_time is None:
                end_time = current_time
                print(f"End set at {format_time(end_time)} s")
                break  # Both points set

    cv2.destroyAllWindows()

    if start_time is None or end_time is None or end_time <= start_time:
        print("No valid selection — keeping full file.")
        return mp3_path

    # Perform trim
    return trim_manual(mp3_path, start_time, end_time)


def render_waveform(y, sr, width=1200, height=300):
    """Convert waveform to an OpenCV image for scrubbing."""
    import matplotlib.pyplot as plt
    from io import BytesIO

    fig, ax = plt.subplots(figsize=(width / 100, height / 100))
    ax.plot(np.arange(len(y)) / sr, y, linewidth=0.5)
    ax.set_xlim([0, len(y) / sr])
    ax.set_ylim([-1, 1])
    ax.axis("off")
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    buf.seek(0)
    file_bytes = np.asarray(bytearray(buf.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    return img

