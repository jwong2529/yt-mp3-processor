
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

mouse_x = 0
mouse_click = None

def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_click_x
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
    elif event == cv2.EVENT_LBUTTONDOWN:
        mouse_click_x = x

def trim_interactive(mp3_path: str) -> str:
    print("Loading audio for interactive trim...")
    y, sr = librosa.load(mp3_path, sr=None, mono=True)

    start_time = None
    end_time = None
    pos = 0 
    
    #  Generate base waveform
    waveform_base = render_waveform(y, sr)
    wf_h, wf_w, _ = waveform_base.shape
    
    # Header
    header_h = 100 
    total_h = wf_h + header_h
    
    window_name = "Trim Audio"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

    print(f"Controls: \n  [Mouse]: Click to seek \n  [Keyboard]: Arrow keys to seek \n  [SPACE]: Set Start (Green) then End (Red)\n  [R]: Reset\n  [Q]: Save")

    global mouse_x, mouse_click_x
    mouse_x = 0
    mouse_click_x = None

    while True:
        # Create a black canvas for the whole window
        canvas = np.zeros((total_h, wf_w, 3), dtype=np.uint8)
        
        # Copy waveform into the bottom part
        canvas[header_h:, :] = waveform_base
        
        # Handle seek
        if mouse_click_x is not None:
            ratio = mouse_click_x / wf_w
            pos = int(ratio * len(y))
            mouse_click_x = None

        # Mouse hover line (Yellow)
        cv2.line(canvas, (mouse_x, header_h), (mouse_x, total_h), (0, 255, 255), 1)
        
        # Current position line (Blue)
        x_pos = int((pos / len(y)) * wf_w)
        cv2.line(canvas, (x_pos, header_h), (x_pos, total_h), (255, 0, 0), 2)

        # Start/end Markers
        if start_time is not None:
            s_x = int((start_time * sr / len(y)) * wf_w)
            cv2.line(canvas, (s_x, header_h), (s_x, total_h), (0, 255, 0), 2)
            # Draw marker label in the header area so it doesn't block wave
            cv2.putText(canvas, "START", (s_x - 20, header_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
        if end_time is not None:
            e_x = int((end_time * sr / len(y)) * wf_w)
            cv2.line(canvas, (e_x, header_h), (e_x, total_h), (0, 0, 255), 2)
            cv2.putText(canvas, "END", (e_x - 15, header_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Text info 
        current_sec = pos / sr
        total_sec = len(y) / sr
        
        # Big time display
        time_text = f"Time: {format_time(current_sec)} / {format_time(total_sec)}"
        cv2.putText(canvas, time_text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Guide text
        if start_time is None:
            guide = "Mouse/arrow keys -> Press [SPACE] to set START"
            guide_col = (0, 255, 255)
        elif end_time is None:
            guide = "Mouse/arrow keys -> Press [SPACE] to set END"
            guide_col = (0, 255, 255)
        else:
            guide = "DONE! Press [Q] to Save or [R] to Reset"
            guide_col = (0, 255, 0) 

        cv2.putText(canvas, guide, (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, guide_col, 2)
        
        # Visual divider line between header and wave
        cv2.line(canvas, (0, header_h), (wf_w, header_h), (100, 100, 100), 1)

        cv2.imshow(window_name, canvas)

        key = cv2.waitKey(20) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('r'):
            start_time = None
            end_time = None
            print("Selection reset.")
        elif key in [81, 2, 2424832]:
            pos = max(pos - sr, 0)
        elif key in [83, 3, 2555904]:
            pos = min(pos + sr, len(y) - 1)
        elif key == 32:  # SPACE
            current_t = pos / sr
            if start_time is None:
                start_time = current_t
                print(f"Start set at {format_time(start_time)}")
            elif end_time is None:
                if current_t > start_time:
                    end_time = current_t
                    print(f"End set at {format_time(end_time)}")
                else:
                    print("End time must be after start time.")

    cv2.destroyAllWindows()

    if start_time is None or end_time is None:
        print("Trimming cancelled or incomplete. Keeping original.")
        return mp3_path

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

