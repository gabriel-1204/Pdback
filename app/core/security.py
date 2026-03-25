#JWT 인증 미들웨어

from jwt import encode, decode
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from app.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

#비밀번호 해시
#사용자가 비밀번호 입력하면 변환해서 db에 저장
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#비밀번호 검증
#사용자가 입력한 비밀번호와 db에 저장된 해시값을 비교해서 맞으면 T, 틀리면 F(bool)
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

#access_token 발급
def create_access_token(data: dict) -> str:
    encode_data = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30) #minutes, hours, days로 변경, 리프레시 토큰 구현 후 연장 예정
    encode_data.update({"exp": expire})
    return encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)

#토큰 검증
def decode_token(token: str) -> dict:
    return decode(token, SECRET_KEY, algorithms=[ALGORITHM])