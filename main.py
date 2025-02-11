# 아래 코드들 작업 설명
# ! 주의사항이나 에러가 발생해 수정이 필요한 사항에 추가
# ? 궁금점이나 수정이 필요한 부분이 있는 경우
# // 해결한 사항
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.db import create_db_and_tables
from app.io import *
import os
from fastapi.middleware.cors import CORSMiddleware
from app.handlers import (auth_handler,
                          chat_handlers,
                          comment_handlers,
                          product_handler)

# FastAPI 애플리케이션 생성
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    create_upload_dir()

app.include_router(auth_handler.router)
app.include_router(chat_handlers.router)
app.include_router(comment_handlers.router)
app.include_router(product_handler.router)

# app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ? react 사용을 위한 CORS 설정
# # 허용할 출처(origin) 목록
# origins = [
#     "http://localhost:3000",  # React 개발 서버
#     "http://127.0.0.1:3000",  # 로컬호스트 IP
#     "https://yourdomain.com",  # 실제 배포된 프론트엔드 URL (필요 시 추가)
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,  # 허용할 도메인 목록
#     allow_credentials=True,  # 쿠키 포함 여부
#     allow_methods=["*"],  # 허용할 HTTP 메서드 (GET, POST, PUT 등)
#     allow_headers=["*"],  # 허용할 HTTP 헤더
# )
