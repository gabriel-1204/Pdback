from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.core.security import decode_token

bearer = HTTPBearer()

# 현재 로그인한 유저 확인
def get_current_user(cred: HTTPAuthorizationCredentials = Depends(bearer)):
    """JWT 토큰 검증 후 현재 로그인한 사용자 ID 반환"""
    token = cred.credentials

    try:
        payload = decode_token(token)

    #except Exception은 모든에러를 잡아서 서버에러도 숨겨질 수 있어 JWT에러를 잡기위해 두 에러 사용
    #ExpiredSignatureError : 토큰 만료될 때, InvalidTokenError : 토큰이 가짜거나 잘못됐을 때
    except (ExpiredSignatureError, InvalidTokenError):
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="토큰에 사용자 ID가 없습니다.")
    
    return user_id