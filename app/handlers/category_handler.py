from fastapi import APIRouter, HTTPException, Depends, Query, Body
from app.db import get_db_session
from app.models.user_and_product_model import *
from sqlmodel import Session, select
from typing import List

router = APIRouter(
    prefix="/categories"
)

class CategoryRequest(BaseModel):
    name: str

# 전체 카테고리 목록 조회
@router.get("/", status_code=200)
def get_categories(db: Session = Depends(get_db_session)) -> List[Category]:
    categories = db.exec(select(Category)).all()
    return categories

# 새로운 카테고리 추가
@router.post("/", status_code=201)
def create_category(
    categoryRequest: CategoryRequest = Body(...),
    db: Session = Depends(get_db_session)
) -> Category:
    
    # 이미 존재하는 카테고리인지 확인
    existing_category = db.exec(select(Category).where(Category.name == categoryRequest.name)).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="이미 존재하는 카테고리입니다.")

    new_category = Category(name=categoryRequest.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category
