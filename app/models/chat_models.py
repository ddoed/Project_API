# app/models/chat_models.py
from sqlmodel import Field, SQLModel
from pydantic import BaseModel
from datetime import *
from typing import Optional

# 채팅방 모델
class ChatRoom(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    created_at: datetime = Field(default_factory=datetime.now)

    chat_seller: int = Field(foreign_key="user.id")
    chat_buyer: int = Field(foreign_key="user.id")

# 메세지 모델
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chatroom_id: int = Field(foreign_key="chatroom.id")
    sender_id: int = Field(foreign_key="user.id")
    receiver_id: int = Field(foreign_key="user.id", nullable=True)
    content: str
    sent_at: datetime = Field(default_factory=datetime.now)

# 채팅에 관한 응답 모델들
class ChatRoomResponse(BaseModel):
    id: int
    product_id: int
    created_at: datetime
    chat_seller: int
    chat_buyer: int

class MessageResponse(BaseModel):
    id: int
    chatroom_id: int
    sender_id: int
    receiver_id: Optional[int]
    content: str
    sent_at: datetime
    
class ReqChatroom(BaseModel):
    user_id: int

class RespChatRoom(BaseModel):
    chatrooms : list[ChatRoom]

class RespChats(BaseModel):
    messages: list[Message]