# app/handlers/chat_handler.py
from fastapi import APIRouter, Depends
from app.db import get_db_session
from app.models.chat_models import *
from app.models.user_and_product_model import *
from app.handlers.auth_handler import get_current_user
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

# 채팅방 생성
@router.post("/products/{product_id}/chats")
def create_chatroom(
    product_id: int,
    current_user=Depends(get_current_user),
    session=Depends(get_db_session)
    ) -> RespChatRoom:
    chatroom = chat_service.create_or_get_chatroom(session, product_id, current_user.id)
    return RespChatRoom(
        chatrooms=[ChatRoomResponse(
            id=chatroom.id,
            product_id=chatroom.product_id,
            created_at=chatroom.created_at,
            chat_seller=chatroom.chat_seller,
            chat_buyer=chatroom.chat_buyer
        )]
    )

# 채팅방 목록 조회
@router.get("/chats")
def get_chatrooms(
    current_user=Depends(get_current_user),
    session=Depends(get_db_session)):
    chatrooms = chat_service.get_chatrooms(session, current_user.id)
    return RespChatRoom(chatrooms=[
        ChatRoomResponse(
            id=room.id,
            product_id=room.product_id,
            created_at=room.created_at,
            chat_seller=room.chat_seller,
            chat_buyer=room.chat_buyer
        ) for room in chatrooms
    ])

# 채팅방 상세 조회 (메세지 조회)
@router.get("/chats/{chatroom_id}")
def get_chats(
    chatroom_id: int,
    current_user=Depends(get_current_user),
    session=Depends(get_db_session)):
    messages = chat_service.get_chats(session, chatroom_id, current_user.id)
    return RespChats(messages=[
        MessageResponse(
            id=msg.id,
            chatroom_id=msg.chatroom_id,
            sender_id=msg.sender_id,
            receiver_id=msg.receiver_id,
            content=msg.content,
            sent_at=msg.sent_at
        ) for msg in messages
    ])