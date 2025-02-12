# Project_API
- FastAPI를 사용한 프로젝트_당근마켓 API 리버싱
- 백엔드 코드
- [프론트엔드 코드](https://github.com/ddoed/Project_API-front)
---
## 프로젝트 참여자
- 정성우[(qda-sw)](https://github.com/qda-sw)
- 임나빈[(ddoed)](https://github.com/ddoed)
- 박지은[(phlox22)](https://github.com/phlox22)
- 강태진[(Mireutale)](https://github.com/Mireutale)
---
## 개발 버전 관리
```
- v0.1.0 base models & database dependencies(25.02.06)
- v0.1.1 append datetime in Product & make new table Purchase
- v0.1.2 append commnet, product, user/product/{bought/likes} api
- v0.1.3 add product handlers (25.02.07)
- v0.1.4 add commnet handlers
- v0.1.5 add auth handlers (25.02.09)
- v0.1.6 update models & add chat handlers
- v0.1.7 add likes, bought handlers & merge (25.02.10)
- v0.1.8 add front setup files
- v0.1.9 add front my_page, sales, boughts, likes & img
- v0.2 split module
```
---
## 실행 테스트
```
> CMD
가상환경 구성
python -m venv .venv

가상환경 실행
.venv\Scripts\activate.bat

라이브러리 설치
pip install "fastapi[standard]"
pip install bcrypt
pip install sqlmodel
pip install python-jose
pip install pydantic
pip install python-dotenv
pip install websockets

서버 실행
fastapi dev main.py
```

## carrot.db
테스트용 db

## frontend - backend
```
homepage
│  ├── sign_in
│        ├── sign_up
│
├── mypage
│  ├── modify_page
│  ├── my_sales
│      ├── regis_product
│          ├── modify_product
│              ├── modify_product_img
│              ├── delete_product_img
│          ├── delete_product
│  ├── my_bought
│  ├── my_likes
│      ├── delete_likes
│  ├── delete_account
│  ├── regis_product
│
├── show_products
│  ├── show_detail_products
│      ├── add_likes
│      ├── add_comments
│          ├── modify_comments
│          ├── delete_comments
│  ├── make_chats
│
│  ├── show_chats
│      ├── show_details_chat
│          ├── chatting

```
---
## ws로 채팅방 메세지 보내기 테스트 코드
const chatroomId = 1; // 존재하는 채팅방 ID로 변경하세요
const ws = new WebSocket(`ws://localhost:8000/chats/${chatroomId}/message`);

ws.onopen = () => {
    console.log('WebSocket 연결 성공');

    // 클라이언트가 보내는 JSON 형식 메시지
    const message = {
        sender_id: 2, // sender_id는 유효한 사용자 ID여야 합니다
        content: "백엔드 공부 파이팅" // 보낼 메시지 내용
    };

    // JSON 메시지를 서버로 전송
    ws.send(JSON.stringify(message));
};

ws.onmessage = (event) => {
    console.log('서버에서 받은 메시지:', event.data);
};

ws.onerror = (error) => {
    console.error('WebSocket 에러:', error);
};

ws.onclose = () => {
    console.log('WebSocket 연결 종료');
};
