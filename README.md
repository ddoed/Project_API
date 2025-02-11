# Project_API
- FastAPI를 사용한 프로젝트_당근마켓 API 리버싱
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
