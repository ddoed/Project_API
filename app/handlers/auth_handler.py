from app.models.models import *
from fastapi import APIRouter,HTTPException,Depends
from app.dependencies import get_db_session
from dataclasses import dataclass
from typing import Optional

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