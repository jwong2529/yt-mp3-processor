
from typing import Optional
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error
from PIL import Image
import io
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils import safe_input

def clear_all_metadata(mp3_path: str) -> None:
    try:
        audio = ID3(mp3_path)
        audio.delete()
        audio.save(v2_version=3)
    except error:
        pass  # No tags yet

def set_basic_metadata(mp3_path: str, title: Optional[str], artist: Optional[str], album: Optional[str]) -> None:
    try:
        tags = EasyID3(mp3_path)
    except error:
        tags = EasyID3()
    if title is not None: tags['title'] = title
    if artist is not None: tags['artist'] = artist
    if album is not None: tags['album'] = album
    tags.save(mp3_path)

def set_cover_from_image(mp3_path: str, image_path: str) -> None:
    img = Image.open(image_path).convert('RGB')
    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=90)
    _set_apic(mp3_path, bio.getvalue())

def _set_apic(mp3_path: str, jpeg_bytes: bytes) -> None:
    try:
        audio = ID3(mp3_path)
    except error:
        audio = ID3()
    # Remove old APIC frames
    audio.delall('APIC')
    audio.add(APIC(
        encoding=3, mime='image/jpeg', type=3, desc='Cover',
        data=jpeg_bytes
    ))
    audio.save(mp3_path, v2_version=3)

# ---------------- CLI helpers ----------------

def edit_metadata_cli(mp3_path: str) -> None:
    clear_all_metadata(mp3_path)
    title = safe_input("Title (blank=skip): ").strip() or None
    artist = safe_input("Artist (blank=skip): ").strip() or None
    album = safe_input("Album (blank=skip): ").strip() or None
    set_basic_metadata(mp3_path, title, artist, album)

# ---------------- GUI ----------------

def edit_metadata_gui(mp3_path: str) -> bool:
    root = tk.Tk()
    root.title("Edit MP3 Metadata")
    root.geometry("360x240")

    # Force the window to the front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)

    vars_ = {k: tk.StringVar() for k in ('title','artist','album')}

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill='both', expand=True)

    def add_row(label, key, row):
        ttk.Label(frm, text=label).grid(row=row, column=0, sticky='w')
        ttk.Entry(frm, textvariable=vars_[key], width=32).grid(row=row, column=1, sticky='ew')

    add_row("Title", 'title', 0)
    add_row("Artist", 'artist', 1)
    add_row("Album", 'album', 2)

    cover_path = tk.StringVar()
    cover_was_set = False

    def choose_cover():
        path = filedialog.askopenfilename(title="Choose cover image", filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if path:
            cover_path.set(path)

    def do_clear():
        try:
            clear_all_metadata(mp3_path)

            # Clear visible GUI fields
            for key in vars_:
                vars_[key].set("")
            cover_path.set("")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_save():
        nonlocal cover_was_set
        try:
            t = vars_['title'].get().strip() or None
            a = vars_['artist'].get().strip() or None
            al = vars_['album'].get().strip() or None
            set_basic_metadata(mp3_path, t, a, al)
            if cover_path.get():
                set_cover_from_image(mp3_path, cover_path.get())
                cover_was_set = True
            # Auto-close GUI window
            root.quit()
            root.destroy()
            root.update()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    frm.grid_columnconfigure(1, weight=1)
    ttk.Button(frm, text="Choose Cover...", command=choose_cover).grid(row=3, column=0, pady=8, sticky='w')
    ttk.Label(frm, textvariable=cover_path, foreground="#666").grid(row=3, column=1, sticky='w')
    ttk.Button(frm, text="Clear All", command=do_clear).grid(row=4, column=0, pady=8, sticky='w')
    ttk.Button(frm, text="Save", command=do_save).grid(row=4, column=1, pady=8, sticky='e')

    root.mainloop()
    return cover_was_set
