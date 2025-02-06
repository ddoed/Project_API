from fastapi import FastAPI
from app.dependencies import get_db_session, create_db_and_tables
from app.models import User, Product, Category, ProductImage, Likes, Comment  # 모델들을 불러옵니다.

# FastAPI 애플리케이션 생성
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
