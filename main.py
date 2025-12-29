
import os
import shutil
from tkinter import Tk, filedialog
from config import get_save_dir, project_tmp_dir
from utils import safe_filename, input_float, confirm, safe_input
from search import is_url, search_youtube, select_result
from downloader import download_best_audio
from trim import trim_manual, trim_interactive
from metadata import edit_metadata_cli, edit_metadata_gui, set_cover_from_image, clear_all_metadata
from cover_art import extract_frame_to_jpeg

def choose_search() -> str:
    q = safe_input("Enter YouTube URL or keywords: ").strip()
    if is_url(q):
        return q
    results = search_youtube(q, limit=8)
    chosen = select_result(results)
    if not chosen:
        raise SystemExit("Cancelled.")
    return chosen['link']

def parse_time_input(s: str) -> float:
    """Parse a time string in s or mm:ss format into total seconds."""
    s = s.strip()
    if not s:
        return 0.0
    if ':' in s:
        parts = s.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid time format: {s}")
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    return float(s)

def maybe_trim(mp3_path: str) -> str:
    if not confirm("Trim audio? "):
        return mp3_path
    mode = safe_input("Trim mode: [1] Manual times  [2] Interactive waveform  (Enter 1/2): ").strip() or "1"
    if mode == "1":
        start = input_float("Start (s, blank=0): ")
        end = input_float("End (s, blank=end): ")
        return trim_manual(mp3_path, start, end)
    else:
        return trim_interactive(mp3_path)

def maybe_metadata(mp3_path: str) -> bool:
    if not confirm("Edit/clear metadata? "):
        return False
    mode = safe_input("Metadata mode: [1] CLI  [2] GUI  (Enter 1/2): ").strip() or "1"
    # if confirm("Clear all existing tags first? "):
    #     clear_all_metadata(mp3_path)
    if mode == "1":
        edit_metadata_cli(mp3_path)
        return False
    else:
        return edit_metadata_gui(mp3_path)

def maybe_trim(mp3_path: str) -> str:
    if not confirm("Trim audio? "):
        return mp3_path
    mode = safe_input("Trim mode: [1] Manual times  [2] Interactive waveform  (Enter 1/2): ").strip() or "1"
    if mode == "1":
        try:
            raw_start = safe_input("Start (s or mm:ss, blank=0): ").strip()
            start = parse_time_input(raw_start)
            raw_end = safe_input("End (s or mm:ss, blank=end): ").strip()
            end = parse_time_input(raw_end) if raw_end else None
        except ValueError as e:
            print(f"Invalid input: {e}")
            return mp3_path
        return trim_manual(mp3_path, start, end)
    else:
        return trim_interactive(mp3_path)


def maybe_cover(mp3_path: str, url: str) -> None:
    if not confirm("Set cover art? "):
        return
    mode = safe_input(
        "Cover source: [1] Frame from video  [2] Local image file  [3] Interactive frame picker  (Enter 1/2/3): "
    ).strip() or "1"

    tmp_dir = project_tmp_dir()
    cover_path = os.path.join(tmp_dir, "cover.jpg")

    if mode == "1":
        try:
            raw_ts = safe_input("Timestamp (s or mm:ss): ").strip()
            ts = parse_time_input(raw_ts)
            extract_frame_to_jpeg(url, ts, cover_path, tmp_dir=tmp_dir)
            set_cover_from_image(mp3_path, cover_path)
            print("Cover set from frame.")
        except ValueError as e:
            print(f"Invalid timestamp input: {e}")
        except Exception as e:
            print("Frame extraction failed:", e)

    elif mode == "2":
        # Open file picker for image
        Tk().withdraw()  # Hide root window
        p = filedialog.askopenfilename(
            title="Select Cover Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
        )
        if p and os.path.isfile(p):
            try:
                set_cover_from_image(mp3_path, p)
                print("Cover set from file.")
            except Exception as e:
                print("Failed to set cover:", e)
        else:
            print("No file selected; skipping cover.")

    elif mode == "3":
        try:
            from cover_art import pick_frame_interactive  # hypothetical module
            chosen_frame_path = pick_frame_interactive(url, tmp_dir)  # returns path to chosen frame
            if chosen_frame_path and os.path.isfile(chosen_frame_path):
                set_cover_from_image(mp3_path, chosen_frame_path)
                print("Cover set from interactive picker.")
            else:
                print("No frame selected.")
        except ImportError:
            print("Interactive frame picker not available.")
        except Exception as e:
            print("Interactive frame picking failed:", e)


def final_rename_and_save(mp3_path: str) -> str:
    out_dir = get_save_dir()
    default_name = os.path.basename(mp3_path)
    print("Example of naming convention: John Mayer - Human Nature (Michael Jackson Memorial 2009).mp3\n")
    new_name = safe_input(f"Rename file (blank to keep '{default_name}'): ").strip()
    final_name = safe_filename(new_name) + '.mp3' if new_name else default_name
    final_path = os.path.join(out_dir, final_name)
    os.makedirs(out_dir, exist_ok=True)
    # If same path, just keep it; else move/copy
    if os.path.abspath(mp3_path) != os.path.abspath(final_path):
        import shutil
        shutil.copy2(mp3_path, final_path)
    print("Saved:", final_path)
    return final_path

def main():
    url = choose_search()
    tmp_dir = project_tmp_dir()

    try:
        print("\nDownloading best audio → MP3...")
        mp3_path, title = download_best_audio(url, tmp_dir)
        print("Downloaded:", mp3_path)

        mp3_path = maybe_trim(mp3_path)
        cover_set_in_metadata = maybe_metadata(mp3_path)
        if not cover_set_in_metadata:
            maybe_cover(mp3_path, url)

        final_rename_and_save(mp3_path)
        print("\nDone.")

    finally:
        if os.path.isdir(tmp_dir):
            for filename in os.listdir(tmp_dir):
                file_path = os.path.join(tmp_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # remove file or symlink
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # remove subdirectory
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
            print(f"Temporary directory cleared: {tmp_dir}")


if __name__ == "__main__":
    main()
