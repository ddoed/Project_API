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
    prefix="/api/users"
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

# 현재 로그인한 사용자를 가져오기
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_session)):
    jwt_util = JWTUtil()
    payload = jwt_util.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=404,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: int = payload.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=404,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.get(User, user_id)  
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# 토큰 발급
@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
    auth_service: AuthService = Depends(),
    jwt_util: JWTUtil = Depends()
):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = {
        "id": user.id,
        "login_id": user.login_id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "created_at": user.created_at
    }

    access_token = jwt_util.create_token(payload)
    # 사용자 정보와 액세스 토큰을 함께 반환
    return {
        "access_token": access_token,
        "token_type": "bearer",
        **payload
    }

#회원가입
@router.post("/signup")
async def auth_signup(req:AuthSignupReq,
                    db=Depends(get_db_session),
                    jwtUtil:JWTUtil=Depends(),
                    authService:AuthService=Depends()):
    user = authService.signup(db, req.login_id, req.pwd, req.name, req.email)

    if not user:
        raise HTTPException(status_code=400, detail="error")

    payload = {
        "id": user.id,
        "login_id": user.login_id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "created_at": user.created_at
    }

    # 토큰 생성
    token = jwtUtil.create_token(payload)

    # DB에 반영되도록 저장
    user.access_token = token  
    db.add(user)
    db.commit()
    db.refresh(user)

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

