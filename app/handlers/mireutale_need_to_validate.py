from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlmodel import Session, select
from app.dependencies import get_db_session, create_db_and_tables
from app.models import User, Product, Category, ProductImage, Likes, Comment, Purchase  # 모델들을 불러옵니다.
from pydantic import BaseModel

router = APIRouter()

@router.get("/users/{user_id}/bought")
def get_user_bought(user_id: int, db: Session = Depends(get_db_session)):
    # 사용자 ID에 해당하는 구매 내역을 가져옵니다.
    purchases = db.exec(select(Purchase).where(Purchase.user_id == user_id)).all()

    # 각 구매 내역에 대해 상품을 찾아서 반환합니다.
    # 만약 값이 없으면 빈 리스트를 출력
    results = [db.get(Product, purchase.product_id) for purchase in purchases]

    return results

@router.get("/users/{user_id}/likes")
def get_user_likes(user_id: int, db: Session = Depends(get_db_session)):
    # 사용자 ID에 해당하는 좋아요 내역을 가져옵니다.
    like_products = db.exec(select(Likes).where(Likes.user_id == user_id)).all()

    # 각 좋아요 내역에 대해 상품을 찾아서 반환합니다.
    # 만약 값이 없으면 빈 리스트를 출력
    results = [db.get(Product, like_product.product_id) for like_product in like_products]

    return results

# Request body에서 받을 데이터를 위한 Pydantic 모델 정의
class LikeRequest(BaseModel):
    user_id: int  # 사용자의 ID

@router.post("/products/{product_id}/likes")
def post_product_likes_add(product_id: int, like_request: LikeRequest, db: Session = Depends(get_db_session)):
    user_id = like_request.user_id  # JSON body에서 user_id를 추출

    # 상품이 존재하는지 확인
    product = db.get(Product, product_id)
    if not product:
        #상품이 없는경우, 에러 메세지 출력
        raise HTTPException(status_code=404, detail="Product not found")

    # 사용자가 이미 이 상품을 좋아요 한 적이 있는지 확인
    # * Likes 테이블에서 user.id와 product.id가 모두 동일한 값이 있는지 확인
    existing_like = db.exec(select(Likes).where(Likes.user_id == user_id, Likes.product_id == product_id)).first()
    if existing_like:
        # 이미 있는 경우, 에러 메세지 출력
        raise HTTPException(status_code=400, detail="You already liked this product")

    # 좋아요 추가
    new_like = Likes(user_id=user_id, product_id=product_id)
    db.add(new_like)
    db.commit()
    # 새로운 객체가 추가되어 데이터베이스에 남아 있으므로 refresh 수행
    db.refresh(new_like)

    return {"message": "Like added successfully", "like_id": new_like.id}



@router.delete("/products/{product_id}/likes")
def delete_product_likes(product_id: int, user_id: int, db: Session = Depends(get_db_session)):
    # 사용자가 해당 상품에 좋아요를 눌렀는지 확인
    like_to_delete = db.exec(select(Likes).where(Likes.user_id == user_id, Likes.product_id == product_id)).first()
    # 좋아요 한 적이 없는 경우 에러 메세지 출력
    if not like_to_delete:
        raise HTTPException(status_code=404, detail="Like not found.")
    
    # 좋아요 삭제
    db.delete(like_to_delete)
    db.commit()

    return {"message": "Like deleted successfully"}