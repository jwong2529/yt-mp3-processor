
import os
import re
import sys
from typing import Optional

def safe_filename(name: str, max_len: int = 200) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", name).strip()
    return name[:max_len]

def input_float(prompt: str, allow_blank: bool = True) -> Optional[float]:
    s = safe_input(prompt).strip()
    if allow_blank and s == "":
        return None
    try:
        return float(s)
    except ValueError:
        print("Invalid number. Try again.")
        return input_float(prompt, allow_blank)

def confirm(prompt: str) -> bool:
    s = safe_input(f"{prompt} [y/N]: ").strip().lower()
    return s in {"y", "yes"}

def safe_input(prompt: str) -> str:
    while True:
        try:
            return input(prompt)
        except KeyboardInterrupt:
            print("\n")
            try:
                confirm = input("Are you sure you want to quit (y/n): ").strip().lower()
                if confirm in ('y', 'yes'):
                    print("Goodbye!")
                    sys.exit(0)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)

            print("Resuming program...\n")
