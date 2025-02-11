# app/dependency/io.py
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

def create_upload_dir():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

def is_allowed_file(filename: str) -> bool:
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS

def unique_filename(filename: str) -> str:
    ext = filename.split('.')[-1]
    return f"{int(time.time())}_{uuid.uuid4().hex}.{ext}"

async def save_UploadFile(file: UploadFile) -> Optional[str]:
    if not is_allowed_file(file.filename):
        return None

    file_name = unique_filename(file.filename)
    file_path = UPLOAD_DIR / file_name
    if os.path.exists(file_path):
        return None

    with open(file_path, "wb") as file_object:
        data = await file.read()
        file_object.write(data)
    return file_name

def delete_file(file_name: str) -> bool:
    file_path = UPLOAD_DIR / file_name
    if not os.path.exists(file_path):
        return False
    os.remove(file_path)
    return True