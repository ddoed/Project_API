# app/models/auth_models.py
from sqlmodel import Field
from datetime import *
from pydantic import BaseModel,EmailStr
from app.models.user_and_product_model import *

# Request body에서 받을 데이터를 위한 Pydantic 모델 정의
class user_LikeRequest(BaseModel):
    user_id: int  # 사용자의 ID

class AuthLoginReq(BaseModel):
    login_id:str
    pwd:str

class AuthSignupReq(BaseModel):
    login_id:str
    pwd:str
    name:str
    email:EmailStr

class ProfileUpdateRequest(BaseModel):
    login_id: Optional[str]
    username: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    current_password: str