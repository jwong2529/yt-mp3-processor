
import os
import re
from typing import Optional

def safe_filename(name: str, max_len: int = 200) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", name).strip()
    return name[:max_len]

def input_float(prompt: str, allow_blank: bool = True) -> Optional[float]:
    s = input(prompt).strip()
    if allow_blank and s == "":
        return None
    try:
        return float(s)
    except ValueError:
        print("Invalid number. Try again.")
        return input_float(prompt, allow_blank)

def confirm(prompt: str) -> bool:
    s = input(f"{prompt} [y/N]: ").strip().lower()
    return s in {"y", "yes"}
