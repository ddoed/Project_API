from pydantic import BaseModel,EmailStr
from sqlmodel import Field
class AuthLoginReq(BaseModel):
    login_id:str
    pwd:str
    name:str
    email:EmailStr

class AuthSignupReq(BaseModel):
    login_id:str
    pwd:str
    name:str
    email:EmailStr
    
class ProfileUpdateRequest(BaseModel):
    username: str | None = Field(None, min_length=2, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)