import json
from fastapi import WebSocket

class WSManager:
    def __init__(self):
        self.rooms: dict[int, set[WebSocket]] = {}  # 채팅방 ID -> 연결된 WebSocket 목록

    async def connect(self, ws: WebSocket, chatroom_id: int, user_id: int):
        """사용자를 특정 채팅방에 연결"""
        await ws.accept()
        if chatroom_id not in self.rooms:
            self.rooms[chatroom_id] = set()
        self.rooms[chatroom_id].add(ws)

        # ✅ JSON 형식으로 입장 메시지 전송
        message = {
            "type": "enter",
            "chatroom_id": chatroom_id,
            "user_id": user_id,
            "message": f"사용자 {user_id}가 입장했습니다."
        }
        await self.send_to_room(chatroom_id, message)

    async def disconnect(self, ws: WebSocket, chatroom_id: int, user_id: int):
        """사용자가 채팅방에서 나갔을 때"""
        if chatroom_id in self.rooms:
            self.rooms[chatroom_id].discard(ws)
            if not self.rooms[chatroom_id]:  # 방이 비었으면 삭제
                del self.rooms[chatroom_id]

            # ✅ 나갔을 때도 메시지 전송
            message = {
                "type": "exit",
                "chatroom_id": chatroom_id,
                "user_id": user_id,
                "message": f"사용자 {user_id}가 퇴장했습니다."
            }
            await self.send_to_room(chatroom_id, message)

    async def send_to_room(self, chatroom_id: int, message: dict):
        """같은 채팅방에 있는 사용자들에게 메시지 전송"""
        if chatroom_id in self.rooms:
            for ws in self.rooms[chatroom_id]:
                try:
                    await ws.send_json(message)  # 이 함수가 async로 정의되어 있어야 'await' 사용 가능
                except Exception as e:
                    print(f"Error sending message to {chatroom_id}: {e}")

    def is_connected(self, chatroom_id: int) -> bool:
        """채팅방에 연결된 사용자가 있는지 확인"""
        return chatroom_id in self.rooms and bool(self.rooms[chatroom_id])

ws_manager = WSManager()    
