# app/handlers/auth_handler.py
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

# 현재 로그인한 사용자를 가져오는 의존성 함수
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)):
    jwt_util = JWTUtil()
    payload = jwt_util.decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=404,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: int = payload.get("id")  # 수정: "id"를 추출
    if user_id is None:
        raise HTTPException(
            status_code=404,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.get(User, user_id)  # 수정: user_id (id)를 사용하여 조회
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
    auth_service: AuthService = Depends(),
    jwt_util: JWTUtil = Depends()
):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)  # 수정: form_data.username 사용
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # JWT 토큰 생성
    payload = {
        "id": user.id,
        "login_id": user.login_id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "created_at": user.created_at
    }
    access_token = jwt_util.create_token(payload)
    return {"access_token": access_token, "token_type": "bearer"}
#회원가입
@router.post("/signup")
async def auth_signup(req:AuthSignupReq,
                db=Depends(get_db_session),
                jwtUtil:JWTUtil=Depends(),
                authService:AuthService=Depends()):
    #id 중복 확인
    # existiong_user = await db.execute(select(User).where(User.login_id==req.login_id))
    # if existiong_user.scalars().first():
    #     raise HTTPException(status_code=400, detail="User already exists")

    user = authService.signup(db,req.login_id,req.pwd,req.name,req.email)
    if not user:
        raise HTTPException(status_code=400,detail="error")
    payload = {
        "id": user.id,
        "login_id": user.login_id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "created_at": user.created_at
    }

    # JWT 토큰 생성
    user.access_token = jwtUtil.create_token(payload)
    return {
        "id": user.id,
        "login_id": user.login_id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "created_at": user.created_at,
        "access_token": user.access_token
    }
# 로그인
@router.post("/signin")
def auth_signin(req:AuthLoginReq,
                db=Depends(get_db_session),
                jwtUtil:JWTUtil=Depends(),
                authService:AuthService=Depends()):
    user = authService.signin(db,req.login_id,req.pwd)
    if not user:
        raise HTTPException(status_code=401,detail="로그인 실패")
    user.access_token = jwtUtil.create_token(user.model_dump())
    return user

# 내 프로필 조회
@router.get("/{user_id}")
def check_profile(user_id:int,
                  db=Depends(get_db_session)):
    if not user_id : 
        raise HTTPException(status_code=404,detail="Not Found")
    user = db.exec(
        select(User).filter(User.id == user_id)
    ).first()
    
    return user

# 내 프로필 수정
@router.put("/profile")
def update_profile(
    update_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    auth_service: AuthService = Depends()
):
    # 이메일 변경 시 중복 확인
    if update_data.email and update_data.email != current_user.email:
        existing_user = db.exec(select(User).where(User.email == update_data.email)).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    
    # 사용자 정보 업데이트
    if update_data.username:
        current_user.username = update_data.username
    if update_data.email:
        current_user.email = update_data.email
    if update_data.password:
        current_user.password = auth_service.get_hashed_pwd(update_data.password)
    
    # 데이터베이스에 변경사항 저장
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    # 업데이트된 사용자 정보 반환 (비밀번호 제외)
    return {
        "id": current_user.id,
        "login_id": current_user.login_id,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "created_at": current_user.created_at
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
# # 내 판매 내역 조회
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
