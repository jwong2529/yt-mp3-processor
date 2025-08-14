
import os
from dotenv import load_dotenv

load_dotenv()

def get_save_dir() -> str:
    path = os.path.expandvars(os.getenv("SAVE_DIR", "")).strip()
    path = os.path.expanduser(path)
    if not path:
        raise ValueError("SAVE_DIR is not set in your .env file.")
    os.makedirs(path, exist_ok=True)
    return path

def project_tmp_dir() -> str:
    tmp = os.path.join(os.getcwd(), "tmp")
    os.makedirs(tmp, exist_ok=True)
    return tmp
