# app.handlers.ws_handler.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db_session
from app.models.chat_models import ChatRoom, Message, MessageResponse
from app.ws_managers import *
import json
from datetime import datetime

router = APIRouter()

# 쿼리 파라미터에서 user_id를 추출하는 함수
def get_user_id_from_query(ws: WebSocket):
    user_id = ws.query_params.get('user_id')
    if user_id is None:
        raise HTTPException(status_code=400, detail="user_id query parameter is required")
    return int(user_id)

@router.websocket("/api/chats/{chatroom_id}/message")
async def chatroom_websocket(ws: WebSocket, chatroom_id: int, user_id: int = Depends(get_user_id_from_query), session: Session = Depends(get_db_session)):
    """WebSocket을 이용한 실시간 채팅 기능"""

    # 채팅방 존재 여부 확인
    chatroom = session.get(ChatRoom, chatroom_id)
    if not chatroom:
        await ws.close()
        raise HTTPException(status_code=404, detail="Chatroom not found")

    # WebSocket 연결 수락 및 채팅방에 추가
    await ws_manager.connect(ws, chatroom_id, user_id)

    try:
        while True:
            # 클라이언트에서 JSON 메시지 받기
            data = await ws.receive_text()
            try:
                message_data = json.loads(data)  # JSON 파싱
                sender_id = message_data.get("sender_id")
                content = message_data.get("content")

                # sender_id가 올바른지 확인 (채팅방의 seller 또는 buyer여야 함)
                if sender_id not in [chatroom.chat_seller, chatroom.chat_buyer]:
                    await ws.send_json("Error: Invalid sender_id")
                    continue  # 잘못된 요청 무시

                # receiver_id 설정
                receiver_id = chatroom.chat_buyer if sender_id == chatroom.chat_seller else chatroom.chat_seller

                # 메시지를 DB에 저장
                new_message = Message(
                    chatroom_id=chatroom_id,
                    sender_id=sender_id,
                    receiver_id=receiver_id,
                    content=content,
                    sent_at=datetime.now()
                )
                session.add(new_message)
                session.commit()

                # WebSocket 연결이 있는 경우에만 메시지 전송
                if ws_manager.is_connected(chatroom_id):
                    await ws_manager.send_to_room(chatroom_id, f"User {sender_id}: {content}")

            except json.JSONDecodeError:
                await ws.send_text("Error: Invalid message format. Use JSON.")

    except WebSocketDisconnect:
        # WebSocket 연결 종료 시 user_id와 chatroom_id를 전달하여 연결 종료 처리
        print(f"WebSocket 연결 끊김 - user_id: {user_id}, chatroom_id: {chatroom_id}")  # 로그로 확인
        await ws_manager.disconnect(ws, chatroom_id, user_id)
        await ws_manager.send_to_room(chatroom_id, f"사용자가 {user_id} 퇴장했습니다.")


@router.post("/api/chats/{chatroom_id}/messages")
def send_message(
    chatroom_id: int,
    message: MessageResponse,
    session: Session = Depends(get_db_session)):
    print(MessageResponse)
    # 새 메시지 객체 생성
    new_message = Message(
        chatroom_id=chatroom_id,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
        sent_at=datetime.now(),
    )

    # 메시지를 DB에 저장
    session.add(new_message)
    session.commit()
    session.refresh(new_message)

    # WebSocket 연결 상태 확인 후 메시지 전송
    if ws_manager.is_connected(chatroom_id):
        # WebSocket을 통해 이미 연결된 클라이언트에게 메시지를 전송
        ws_manager.send_to_room(chatroom_id, f"User {message.sender_id}: {message.content}")

    return MessageResponse(
        id=new_message.id,
        chatroom_id=new_message.chatroom_id,
        sender_id=new_message.sender_id,
        receiver_id=new_message.receiver_id,
        content=new_message.content,
        sent_at=new_message.sent_at,
    )
