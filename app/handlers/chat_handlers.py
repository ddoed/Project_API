# app/handlers/chat_handler.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.models.chat_models import *
from app.models.user_and_product_model import *
from app.db import get_db_session

router = APIRouter()

# 채팅방 생성
@router.post("/products/{product_id}/chats")
def create_chatroom(product_id:int, reqChat: ReqChatroom,
                    session=Depends(get_db_session)) -> RespChatRoom:
    # product_id에 해당하는 product를 조회하여 판매자 id 가져오기
    product = session.get(Product, product_id)
    # product가 없을 경우 예외처리
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    # 채팅방 생성
    # user_id를 body로 받도록 함
    new_chatroom = ChatRoom(product_id=product_id,
                            chat_seller=product.user_id,
                            chat_buyer=reqChat.user_id,
                            created_at=datetime.now()
    )
    session.add(new_chatroom)
    session.commit()
    session.refresh(new_chatroom)
    return RespChatRoom(chatrooms=[new_chatroom])

# 채팅방 목록 조회
@router.get("/chats")
def get_chatrooms(user_id: int, session=Depends(get_db_session)):
    # 쿼리 파라미터로 use_id를 받아 채팅방 목록 조회
    chatrooms = session.exec(
        select(ChatRoom).where(
            (ChatRoom.chat_seller == user_id) | (ChatRoom.chat_buyer == user_id)
        )
    ).all()
    return RespChatRoom(chatrooms=chatrooms)

# 채팅방 상세 조회 (메세지 조회)
@router.get("/chats/{chatroom_id}")
def get_chats(chatroom_id: int, session=Depends(get_db_session)):
    # 채팅방 조회
    chatroom = session.get(ChatRoom, chatroom_id)
    # 채팅방이 없으면 에러 발생
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chatroom not found")
    # 해당 채팅방의 메세지를 조회하여 반환
    messages = session.exec(
        select(Message).where(Message.chatroom_id == chatroom_id)
    ).all()
    return RespChats(messages=messages)
