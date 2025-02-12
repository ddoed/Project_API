# app/io.py
from fastapi import UploadFile
import os
import uuid
import time
from typing import Optional
from pathlib import Path
import os
from pathlib import Path

# 프로젝트 루트 경로를 기준으로 'uploads' 디렉토리 생성
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
        
def _is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS

def _unique_filename(filename: str) -> str:
    ext = filename.split('.')[-1]
    return f"{int(time.time())}_{uuid.uuid4().hex}.{ext}"

def create_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_file_name(filename: str) -> str:
    if not _is_allowed_file(filename):
        return None
    return _unique_filename(filename)

def save_file(file_name: Path, file_content: bytes) -> None:
    file_path = UPLOAD_DIR / file_name
    if file_path.exists():
        return None
    with open(file_path, "wb") as f:
        f.write(file_content)

def delete_file(file_name: str) -> bool:
    file_path = UPLOAD_DIR / file_name
    if not file_path.exists():
        return False
    os.remove(file_path)
    return True