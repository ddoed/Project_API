# #app/db.py
from sqlmodel import Session, create_engine, SQLModel

# 데이터베이스 URL 설정 (여기서는 SQLite 사용)
db_file_name = "carrot.db"
db_url = f"sqlite:///./{db_file_name}"

# 여러 스레드에서 SQLite 연결을 공유할 수 있도록 설정
db_conn_args = {"check_same_thread": False}
# 데이터베이스 엔진 생성, 데이터베이스와의 실제 연결 관리
db_engine = create_engine(db_url, connect_args=db_conn_args)

# 데이터베이스와의 연결 관리를 Session으로 수행
def get_db_session():
    with Session(db_engine) as session:
        yield session

# 데이터베이스 테이블 생성 함수
def create_db_and_tables():
    SQLModel.metadata.create_all(db_engine)
