# 아래 코드들 작업 설명
# * 코드 한줄 작동 방식 설명
# ! 주의사항이나 에러가 발생해 수정이 필요한 사항에 추가
# ? 궁금점이나 수정이 필요한 부분이 있는 경우
# // 해결한 사항
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.dependencies import get_db_session, create_db_and_tables
from app.models.models import User, Product, Category, ProductImage, Likes, Comment, Purchase  # 모델들을 불러옵니다.
from pydantic import BaseModel
from app.handlers import (auth_handler,
                          chat_handlers,
                          comment_handlers,
                          jsw_need_to_validate)

# FastAPI 애플리케이션 생성
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth_handler.router)
app.include_router(chat_handlers.router)
app.include_router(comment_handlers.router)
app.include_router(jsw_need_to_validate.router)

# 정적 파일 (CSS, JS, 이미지 등) 제공
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 정적 파일을 서빙할 static 폴더 등록
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "홈페이지"})

@app.get("/my_page")
async def my_page(request: Request):
    user_data = {
        "name": "홍길동",
        "email": "hong@example.com",
        "profile_pic": "https://via.placeholder.com/150"
    }
    return templates.TemplateResponse("my_page.html", {"request": request, "user": user_data})

@app.get("/sales_list")
async def sales_list(request: Request):
    return templates.TemplateResponse("sales_list.html", {"request": request})

@app.get("/bought_list")
async def bought_list(request: Request):
    return templates.TemplateResponse("bought_list.html", {"request": request})

@app.get("/likes_list")
async def likes_list(request: Request):
    return templates.TemplateResponse("likes_list.html", {"request": request})
