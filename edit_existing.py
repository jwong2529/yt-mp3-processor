import os
from tkinter import Tk, filedialog
from config import get_save_dir
from utils import safe_filename, confirm
from metadata import edit_metadata_cli, edit_metadata_gui, clear_all_metadata, set_cover_from_image

def pick_existing_mp3():
    save_dir = get_save_dir()
    files = [f for f in os.listdir(save_dir) if f.lower().endswith(".mp3")]
    if not files:
        print(f"No MP3 files found in {save_dir}")
        raise SystemExit

    print("\nAvailable MP3 files:")
    for i, f in enumerate(files, start=1):
        print(f"[{i}] {f}")
    choice = input("Select a file number: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(files)):
        print("Invalid choice.")
        raise SystemExit
    return os.path.join(save_dir, files[int(choice) - 1])

def maybe_metadata(mp3_path):
    if not confirm("Edit/clear metadata? "):
        return
    if confirm("Clear all existing tags first? "):
        clear_all_metadata(mp3_path)
    mode = input("Metadata mode: [1] CLI  [2] GUI  (Enter 1/2): ").strip() or "1"
    if mode == "1":
        edit_metadata_cli(mp3_path)
    else:
        edit_metadata_gui(mp3_path)

def maybe_cover(mp3_path):
    if not confirm("Set or replace cover art? "):
        return

    # File picker for image
    Tk().withdraw()  # Hide root window
    img_path = filedialog.askopenfilename(
        title="Select Cover Image",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
    )

    if img_path and os.path.isfile(img_path):
        try:
            set_cover_from_image(mp3_path, img_path)
            print("Cover art updated.")
        except Exception as e:
            print(f"Failed to set cover: {e}")
    else:
        print("No file selected; skipping cover.")

def maybe_rename(mp3_path):
    save_dir = get_save_dir()
    default_name = os.path.basename(mp3_path)
    new_name = input(f"Rename file (blank to keep '{default_name}'): ").strip()
    if not new_name:
        return
    final_name = safe_filename(new_name)
    final_path = os.path.join(save_dir, final_name)
    if os.path.abspath(mp3_path) != os.path.abspath(final_path):
        os.rename(mp3_path, final_path)
        print(f"Renamed to: {final_path}")
    else:
        print("Name unchanged.")

def main():
    mp3_path = pick_existing_mp3()
    maybe_metadata(mp3_path)
    maybe_cover(mp3_path)
    maybe_rename(mp3_path)
    print("\nDone editing.")

if __name__ == "__main__":
    main()
