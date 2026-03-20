from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_token

bearer = HTTPBearer()

# 현재 로그인한 유저 확인
def get_current_user(cred: HTTPAuthorizationCredentials = Depends(bearer)):
    token = cred.credentials

    try:
        payload = decode_token(token)

    except:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    
    return payload["sub"]