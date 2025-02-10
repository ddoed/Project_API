from datetime import datetime,timedelta,timezone
from jose import jwt

SECRET_KEY = "1234"
ALGORITHMS = "HS256"
class JWTUtil:
    def create_token(self,payload=dict, 
                     expires_delta: timedelta|None=timedelta(minutes=30))->str: #유효기간 30분
        payload_to_encode = payload.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        payload_to_encode.update({'exp': expire})
        return jwt.encode (payload_to_encode,SECRET_KEY,algorithm=ALGORITHMS)
    # 2. token 문자열로 payload 만드는 함수
    def decode_token(self, token:str)->dict|None:
        try:
            payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHMS])
            if payload is not None:
                nNow = int(time.time())
                nExpireAt = payload.get('exp', 0)
                if nExpireAt < nNow:
                    return None
        except:
            pass
        return None
    