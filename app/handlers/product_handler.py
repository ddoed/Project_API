from app.models.models import *
from fastapi import APIRouter,HTTPException,Depends
from app.dependencies import get_db_session
from sqlmodel import Session, select

router = APIRouter(
    prefix="/products"
)

# 물건에 좋아요 추가
@router.post("/products/{product_id}/likes")
def post_product_likes_add(product_id: int, like_request: user_LikeRequest, db: Session = Depends(get_db_session)):
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

    return {"message": "Like added successfully", "like_id": new_like.id, "liker_id": new_like.user_id}

# 좋아요 누른 물건 좋아요 삭제
@router.delete("/products/{product_id}/likes")
def delete_product_likes(product_id: int, delete_request: user_LikeRequest, db: Session = Depends(get_db_session)):
    user_id = delete_request.user_id

    # 사용자가 해당 상품에 좋아요를 눌렀는지 확인
    like_to_delete = db.exec(select(Likes).where(Likes.user_id == user_id, Likes.product_id == product_id)).first()
    # 좋아요 한 적이 없는 경우 에러 메세지 출력
    if not like_to_delete:
        raise HTTPException(status_code=404, detail="Like not found.")
    
    # 좋아요 삭제
    db.delete(like_to_delete)
    db.commit()

    return {"message": "Like deleted successfully", "like_id": like_to_delete.id, "liker_id": like_to_delete.user_id}