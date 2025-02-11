# app/models/chat_models.py
from sqlmodel import Field, SQLModel
from pydantic import BaseModel
from datetime import *

# 채팅방 모델
class ChatRoom(SQLModel, table=True):
    id: int = Field(primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    created_at: datetime

    chat_seller: int = Field(foreign_key="user.id")
    chat_buyer: int = Field(foreign_key="user.id")

# 메세지 모델
class Message(SQLModel, table=True):
    id: int = Field(primary_key=True)
    chatroom_id: int = Field(foreign_key="chatroom.id")
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id")
    content: str
    sent_at: datetime

# 채팅에 관한 응답 모델들
class ReqChatroom(BaseModel):
    user_id: int

class RespChatRoom(BaseModel):
    chatrooms : list[ChatRoom]

class RespChats(BaseModel):
    messages: list[Message]