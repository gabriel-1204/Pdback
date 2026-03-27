from datetime import datetime, timedelta

from bson import ObjectId
from fastapi import HTTPException
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.config import KST
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database import get_database
from app.domain.user.schemas import UserResponse


# 회원가입
# 이메일(아이디) 체크- 중복방지, 비밀번호해시, 디비저장, 토큰, 포지션(선택값)
async def register(username:str, email:str, password:str, position:str|None = None) -> dict:
    """이메일 중복 확인 후 회원가입 처리"""
    db = get_database()

    existing_user = await db["users"].find_one({"email" : email})
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    password_hash = hash_password(password)
    now = datetime.now(KST)
    result = await db["users"].insert_one({
        "username" : username,
        "email" : email,
        "password_hash" : password_hash,
        "role" : "candidate",
        "is_active" : True,
        "created_at" : now,
        "updated_at" : now,
        "last_login" : None,
        "position" : position,
        "refresh_token" : None,})

    user_id = str(result.inserted_id)
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})

    # DB에 refresh_token 저장
    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"refresh_token": refresh_token}})

    return {"access_token": access_token, "refresh_token": refresh_token}


# 로그인
# 사용자 찾고 비밀번호 확인- 이메일/비번 오류, 사용자 없을 시 에러발생, 토큰
async def login(email:str, password:str) -> dict: #토큰 두개 반환되어 str->dict
    """이메일/비밀번호 확인 후 엑세스 토큰 반환"""
    db = get_database()
    user = await db["users"].find_one({"email" : email})

    if not user:  # 사용자 존재 여부 확인 (없으면 비밀번호 검증 자체가 불필요)
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")
    if not user["is_active"]:  # 비활성화 계정 차단 (비밀번호가 맞아도 로그인 불가)
        raise HTTPException(status_code=403, detail="비활성화된 계정입니다.")
    if not verify_password(password, user["password_hash"]):  # 비밀번호 검증 (활성 계정에 한해서만 수행)
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")

    user_id = str(user["_id"])
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})

    # DB에 last_login, refresh_token 저장
    await db["users"].update_one(
        {"_id" : ObjectId(user_id)},
        {"$set" : {"last_login" : datetime.now(KST),"refresh_token": refresh_token }})

    return {"access_token": access_token, "refresh_token": refresh_token}


# 로그아웃 : 리프레시토큰을 none으로
async def logout(user_id:str) -> dict:
    """리프레시 토큰을 None으로 초기화하여 로그아웃 처리"""
    db = get_database()
    await db["users"].update_one({"_id" : ObjectId(user_id)},{"$set" : {"refresh_token" : None}})

    return {"message":"로그아웃되었습니다."}

# 내 정보 조회
# db에서 사용자 찾아서 반환
async def get_me(user_id: str) -> UserResponse:
    """현재 로그인한 사용자의 정보 반환"""
    db = get_database()
    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    user["_id"] = str(user["_id"])
    return UserResponse.model_validate(user)

# 프로필수정(이름, 비밀번호 변경)
async def update_me(
    user_id: str,
    username: str | None = None,
    position: str | None = None,
    current_password: str | None = None,
    new_password: str | None = None
) -> UserResponse:
    """현재 로그인한 사용자의 프로필(이름/비밀번호)을 수정"""
    db = get_database()
    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # 기본필드
    fields = {"updated_at" : datetime.now(KST)}
    if username is not None:
        fields["username"] = username

    # 희망직무 수정
    if position is not None:
        fields["position"] = position

    # 비밀번호는 수정 시 검증
    if new_password:
        if not current_password:
            raise HTTPException(status_code=400, detail="현재 비밀번호를 입력해주세요.")
        if not verify_password(current_password, user["password_hash"]):
            raise HTTPException(status_code=400, detail="현재 비밀번호가 일치하지 않습니다.")

        fields["password_hash"] = hash_password(new_password)

    await db["users"].update_one({"_id":ObjectId(user_id)}, {"$set":fields})

    return await get_me(user_id)

# 회원탈퇴
async def delete_me(user_id:str, password : str) -> dict:
    """비밀번호 재확인 후 회원탈퇴 처리"""
    db = get_database()

    # 비밀번호 재확인
    user = await db["users"].find_one({"_id":ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    # 탈퇴
    result = await db["users"].delete_one({"_id":ObjectId(user_id)})
    # 예외상황 발생 시 오류처리(예, 탈퇴요청이 두번 들어온 경우 오류)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="탈퇴한 계정입니다.")

    return {"message":"회원탈퇴가 완료되었습니다."}

# 리프레시 토큰 - 새토큰발급해서 자동 로그인 연장
async def refresh(refresh_token: str) -> dict:
    """리프레시 토큰 검증 후 새 엑세스 토큰 발급"""
    try:
        payload = decode_token(refresh_token)
        user_id = payload["sub"]

    except (ExpiredSignatureError, InvalidTokenError):
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    db = get_database()
    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    # DB에 저장된 토큰과 비교해서 일치할때만 발급
    if user["refresh_token"] != refresh_token:
        raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰입니다.")

    new_access_token = create_access_token({"sub": user_id})
    new_refresh_token = create_refresh_token({"sub": user_id})

    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"last_login": datetime.now(KST),"refresh_token": new_refresh_token}})

    return {"access_token": new_access_token, "refresh_token": new_refresh_token}

# 인터뷰
async def get_my_stats(user_id: str) -> dict:
    db = get_database()

    # 월~일 기준으로 일주일 잡았어요
    # 월0 화1 ~ 일6 숫자로 나오고 오늘 - 요일숫자 하면 이번주 월요일 날짜가 나와요.
    today = datetime.now(KST)
    monday = today - timedelta(days=today.weekday())
    week_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)

    # 이번주 면접횟수
    weekly_count = await db["interviews"].count_documents({
        "user_id": user_id,
        "created_at": {"$gte": week_start} #인터뷰컬렉션의 created_at
    })

    return {"weekly_interviews": weekly_count}
