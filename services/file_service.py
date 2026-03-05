import os
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def save_file(file, filename):
    path = UPLOAD_DIR / filename
    with open(path, "wb") as f:
        f.write(file)
    return path