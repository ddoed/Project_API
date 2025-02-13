import json
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, WebSocket, WebSocketDisconnect
from datetime import datetime
from app import ws_managers
from app.models.chat_models import *
from app.models.user_and_product_model import *
from app.db import get_db_session

class ChatService:
    # 채팅방 ID로 채팅방 조회
    def get_chatroom_by_id(self, db: Session, chatroom_id: int):
        chatroom = db.get(ChatRoom, chatroom_id)
        if not chatroom:
            raise HTTPException(status_code=404, detail="Chatroom not found")
        return chatroom
    
    # 사용자가 채팅방에 속해 있는지 확인
    def check_chatroom_access(self, chatroom: ChatRoom, user_id: int):
        if user_id not in [chatroom.chat_seller, chatroom.chat_buyer]:
            raise HTTPException(status_code=403, detail="Permission denied")
    
    # 채팅방 생성
    def create_or_get_chatroom(self, db: Session, product_id: int, user_id: int):
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        # 이미 존재하는 채팅방 확인
        existing_chatroom = db.exec(
            select(ChatRoom).where(
                (ChatRoom.product_id == product_id) &
                ((ChatRoom.chat_seller == user_id) | (ChatRoom.chat_buyer == user_id))
            )
        ).first()
        # 이미 채팅방이 존재할 경우 기존 채팅방 반환환
        if existing_chatroom:
            return existing_chatroom
        # 없으면 채팅방 새로 생성
        new_chatroom = ChatRoom(
            product_id=product_id,
            chat_seller=product.user_id,
            chat_buyer=user_id,
            created_at=datetime.now()
        )
        db.add(new_chatroom)
        db.commit()
        db.refresh(new_chatroom)
        
        return new_chatroom
    
    # 특정 사용자의 채팅방 목록 조회
    def get_chatrooms(self, db: Session, user_id: int):
        chatrooms = db.exec(
            select(ChatRoom).where(
                (ChatRoom.chat_seller == user_id) | (ChatRoom.chat_buyer == user_id)
            )
        ).all()
        return chatrooms
    
    # 특정 채팅방의 메세지 조회
    def get_chats(self, db: Session, chatroom_id: int, user_id: int):
        chatroom = self.get_chatroom_by_id(db, chatroom_id)
        self.check_chatroom_access(chatroom, user_id)
        
        messages = db.exec(
            select(Message).where(Message.chatroom_id == chatroom_id)
        ).all()
        
        return messages