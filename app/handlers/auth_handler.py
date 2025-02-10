from app.models.models import *
from fastapi import APIRouter,HTTPException,Depends
from app.dependencies import get_db_session
from dataclasses import dataclass
from typing import Optional
from sqlmodel import Session, select

router = APIRouter(
    prefix="/users"
)

@dataclass
class AuthLginReq:
    login_id : str
    password : str

@dataclass
class AuthResp:
    jwn_token : Optional[str]
    err_msg :Optional[str]

@dataclass
class ProfileResp:
    profile : Optional[User]
    err_str: Optional[str]
    
#회원가입
@router.post("/signup",status_code=201)
def signup(user:User)-> AuthResp:
    return {"jwn_token":"임시 토큰"} 
    
# 로그인
@router.post("/login",status_code=201)
def signin(user:AuthLginReq)->AuthResp:
    return{"jwn_token":"임시 토큰"}

# 내 프로필 조회
@router.get("/{user_id}")
def check_profile(user_id:int,
                  db=Depends(get_db_session))->ProfileResp:
    if not user_id : 
        raise HTTPException(status_code=404,detail="Not Found")
    user = db.exec(
        select(User).filter(User.id == user_id)
    ).first()
    
    return {"profile":user}

# 내 프로필 수정
@router.put("/{user_id}")
def update_profile(user_id:int,
                    db=Depends(get_db_session)):
    user=db.get(User,user_id)
    if not User:
        raise HTTPException(status_code=404,
                            detail="Not Found")
    return {"Ok":"Profile Update"}

# 회원 탈퇴
@router.delete("/{user_id}")
def delete_profile(user_id:str,
                    db=Depends(get_db_session)):
    user = db.get(User,user_id)
    if not User:
        raise HTTPException(status_code=404,
                            detail="Not Found")
    return {"Ok":"Profile deleted"}

# 내 판매 내역 조회
@router.get("/{user_id}/selling")
def check_my_selling_list(user_id:str,
                          db = Depends(get_db_session)):
    user = db.get(User,user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not Found")
    selling_list = user.products
    return {
        "my selling list": selling_list
    }

# 내 구매 내역 조회
@router.get("/{user_id}/bought")
def get_user_bought(user_id: int, db: Session = Depends(get_db_session)):
    # 사용자 ID에 해당하는 구매 내역을 가져옵니다.
    purchases = db.exec(select(Purchase).where(Purchase.user_id == user_id)).all()

    # 각 구매 내역에 대해 상품을 찾아서 반환합니다.
    # 만약 값이 없으면 빈 리스트를 출력
    results = [db.get(Product, purchase.product_id) for purchase in purchases]

    return results

# 내 좋아요 내역 조회
@router.get("/{user_id}/likes")
def get_user_likes(user_id: int, db: Session = Depends(get_db_session)):
    # 사용자 ID에 해당하는 좋아요 내역을 가져옵니다.
    like_products = db.exec(select(Likes).where(Likes.user_id == user_id)).all()

    # 각 좋아요 내역에 대해 상품을 찾아서 반환합니다.
    # 만약 값이 없으면 빈 리스트를 출력
    results = [db.get(Product, like_product.product_id) for like_product in like_products]

    return results