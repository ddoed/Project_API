from app.handlers.auth_handler import get_current_user
from app.models.chat_models import *
from fastapi import APIRouter, HTTPException, Depends, status
from app.db import get_db_session
from app.models.auth_models import *
from app.jwt_util import JWTUtil
from app.services.auth_service import AuthService
from app.models.user_and_product_model import *
from sqlmodel import select, Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/users"
)

# 판매 내역 조회
@router.get("/selling", status_code=200)
def check_my_selling_list(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    ):
    # 현재 로그인한 사용자의 판매 내역 조회
    selling_list = db.exec(select(Product).where(Product.user_id == current_user.id)).all()
    return {"my_selling_list": selling_list}


# 내 좋아요 내역 조회
@router.get("/{user_id}/likes")
def get_user_likes(user_id: int, db: Session = Depends(get_db_session)):
    # 사용자 ID에 해당하는 좋아요 내역을 가져옵니다.
    like_products = db.exec(select(Likes).where(Likes.user_id == user_id)).all()

    # 각 좋아요 내역에 대해 상품을 찾아서 반환합니다.
    # 만약 값이 없으면 빈 리스트를 출력
    results = [db.get(Product, like_product.product_id) for like_product in like_products]

    return results


#프로필 수정
@router.put("/profile")
def update_profile(
    update_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    auth_service: AuthService = Depends(),
    jwt_util: JWTUtil = Depends()
):
    # 현재 비밀번호 확인 (비밀번호 변경 시)
    if update_data.password:
        if not auth_service.verify_pwd(update_data.current_password, current_user.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
        current_user.password = auth_service.get_hashed_pwd(update_data.password)
    
    # 이메일 중복 확인
    if update_data.email and update_data.email != current_user.email:
        existing_user = db.exec(select(User).where(User.email == update_data.email)).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    
    # 로그인 ID 중복 확인
    if update_data.login_id and update_data.login_id != current_user.login_id:
        existing_user = db.exec(select(User).where(User.login_id == update_data.login_id)).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login ID already in use")
    
    # 사용자 정보 업데이트
    if update_data.username and update_data.username != current_user.username:
        current_user.username = update_data.username
    if update_data.email and update_data.email != current_user.email:
        current_user.email = update_data.email
    if update_data.login_id and update_data.login_id != current_user.login_id:
        current_user.login_id = update_data.login_id
    
    try:
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the profile")
    
    # 새로운 토큰 생성 (필요한 경우)
    payload = {
        "id": current_user.id,
        "login_id": current_user.login_id,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "created_at": str(current_user.created_at)  # datetime -> string 변환 필요
    }
    new_access_token = jwt_util.create_token(payload)

    # 업데이트된 사용자 정보와 새 토큰 반환
    return {
        "id": current_user.id,
        "login_id": current_user.login_id,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "created_at": str(current_user.created_at),
        "access_token": new_access_token  # 새 토큰 포함
    }


# 회원 탈퇴
@router.delete("/profile")
def delete_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    # 사용자 확인
    user = db.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # 데이터베이스에서 사용자 삭제
    db.delete(user)
    db.commit()

    return {"message": "Profile deleted successfully"}