# 아래 코드들 작업 설명
# * 코드 한줄 작동 방식 설명
# ! 주의사항이나 에러가 발생해 수정이 필요한 사항에 추가
# ? 궁금점이나 수정이 필요한 부분이 있는 경우
# // 해결한 사항
from fastapi import FastAPI, Depends, HTTPException
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
