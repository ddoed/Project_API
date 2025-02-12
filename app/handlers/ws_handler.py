# app.handlers.ws_handler.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db_session
from app.models.chat_models import ChatRoom, Message, MessageResponse
from app.ws_managers import *
import json
from datetime import datetime

router = APIRouter()

@router.websocket("/chats/{chatroom_id}/message")
async def chatroom_websocket(ws: WebSocket, chatroom_id: int, session: Session = Depends(get_db_session)):
    """WebSocket을 이용한 실시간 채팅 기능"""

    # 채팅방 존재 여부 확인
    chatroom = session.get(ChatRoom, chatroom_id)
    if not chatroom:
        await ws.close()
        raise HTTPException(status_code=404, detail="Chatroom not found")

    # WebSocket 연결 수락 및 채팅방에 추가
    await ws_manager.connect(ws, chatroom_id)

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

                # 같은 채팅방에 있는 모든 사용자에게 메시지 전송
                await ws_manager.send_to_room(chatroom_id, f"User {sender_id}: {content}")

            except json.JSONDecodeError:
                await ws.send_text("Error: Invalid message format. Use JSON.")

    except WebSocketDisconnect:
        ws_manager.disconnect(ws, chatroom_id)
        await ws_manager.send_to_room(chatroom_id, "사용자가 퇴장했습니다.")

# HTTP POST 메시지 전송 기능 (WebSocket을 사용하지 않음)
@router.post("/chats/{chatroom_id}/messages")
def send_message(
    chatroom_id: int,
    message: MessageResponse,
    session: Session = Depends(get_db_session),
):
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

    # WebSocket을 통해 메시지를 채팅방에 있는 모든 사용자에게 전달
    # WebSocket을 통해 이미 연결된 클라이언트에게 메시지를 전송 (이 부분은 WebSocket 연결된 상태에서 처리)
    ws_manager.send_to_room(chatroom_id, f"User {message.sender_id}: {message.content}")

    return MessageResponse(
        id=new_message.id,
        chatroom_id=new_message.chatroom_id,
        sender_id=new_message.sender_id,
        receiver_id=new_message.receiver_id,
        content=new_message.content,
        sent_at=new_message.sent_at,
    )