# app/services/auth_service.py
import bcrypt
import time
from sqlmodel import Session,select
from app.models.user_and_product_model import User
from fastapi import HTTPException,UploadFile,File
import uuid
from fastapi.responses import JSONResponse
import os
import shutil

class AuthService:
    #1.PassWord 단방향 암호화
    #회원가입 -> password 암호화 -> DB
    def get_hashed_pwd(self, pwd:str)->str : #암호화된 password 돌려주기
        encoded_pwd = pwd.encode("utf-8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(encoded_pwd,salt)
    #2. PassWord 검증
    #로그인 할 때 넣은 password 암호화 -> DB상의 암호화된 password와 비교
    def verify_pwd(self, pwd:str, hpwd:str)->bool: #성공 or 실패 확인 반환
        encoded_pwd = pwd.encode('utf-8')
        return bcrypt.checkpw(password=encoded_pwd,hashed_password=hpwd)
    #3.회원가입때 DB 로직 구성
    # - 가입일시를 만들어서 User.created_at에 넣어주고
    # - (1) Password 암호화 함수를 이용하여 암호화된 패스워드 -> User.pwd에 넣기
    # - DB에 User을 넣는다
    def signup(self, db: Session, login_id: str, pwd: str, name: str, email: str) -> User | None:
        try:
            hashed_pwd = self.get_hashed_pwd(pwd)
            user = User(
                login_id=login_id,
                password=hashed_pwd,
                username=name,
                role='user',
                email=email,
            )
            user.created_at = int(time.time())

            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Signup failed: {str(e)}")

    #4. 로그인 API에서 구현할 DB로직 구현
    # - DB에 저장된 사용자 정보를 불러온다
    # - 클라이언트가 입력한 패스워들 문자열을 암호화하여 DB에 저장된 패스워드와 일치하는지 (2)함수로 검사
    def signin(self,db:Session,login_id:str,password:str)->User|None:
        dbUser = self.get_user_by_name(db,login_id)
        if not dbUser:
            return None
        if not self.verify_pwd(password,dbUser.password):
            return None #검증 실패
        
        return dbUser #검증 성공
    
    def authenticate_user(self, db: Session, login_id: str, password: str):
        user = self.get_user_by_name(db, login_id)
        if not user:
            return None
        if not self.verify_pwd(password, user.password):  # 수정: self.verify_pwd 사용
            return None
        return user

    def get_user_by_name(self, db: Session, login_id: str) -> User | None:
        stmt = select(User).where(User.login_id == login_id)  # SQL 쿼리 작성
        results = db.exec(stmt)  # 쿼리 실행
        user = results.first()  # 첫 번째 결과 반환
        return user