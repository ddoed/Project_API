# Project_API
- FastAPI를 사용한 프로젝트_당근마켓 API 리버싱
---
## 프로젝트 참여자
- 정성우
- 임나빈
- 박지은
- 강태진
---
## 개발 버전 관리
```
- v0.1.0 base models & database dependencies
- v0.1.1 append datetime in Product & make new table Purchase
- v0.1.2 append commnet, product, user/product/{bought/likes} api 
- v0.1.5 pr auth, chat, product and user(likes, bought) handler and models
```
---
## 실행 테스트
```
> CMD
가상환경 구성
- python -m venv .venv

가상환경 실행
-  .venv\Scripts\activate.bat

라이브러리 설치
pip install "fastapi[standard]"
pip install SQLModel

서버 실행
fastapi dev main.py
```
## 해야할 일
1. models.py 내부 모듈 사용 부분 분할(user, product, comment...)
2. jsw_need_val...py 모듈 테스트 후 각 handler 내부로 분할 (정성우님)
3. 관련 코드 테스트 후 notion에 api 결과 작성(박지은님)