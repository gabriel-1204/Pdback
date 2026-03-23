from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_token
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

bearer = HTTPBearer()

# 현재 로그인한 유저 확인
def get_current_user(cred: HTTPAuthorizationCredentials = Depends(bearer)):
    token = cred.credentials

    try:
        payload = decode_token(token)

    #except Exception은 모든에러를 잡아서 서버에러도 숨겨질 수 있어 JWT에러를 잡기위해 두 에러 사용
    #ExpiredSignatureError : 토큰 만료될 때, InvalidTokenError : 토큰이 가짜거나 잘못됐을 때
    except (ExpiredSignatureError, InvalidTokenError):
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    
    return payload["sub"]
