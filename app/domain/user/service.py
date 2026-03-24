from app.database import get_database
from app.domain.user.schemas import UserResponse
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException
from datetime import datetime, timezone
from bson import ObjectId


#회원가입
#이메일(아이디) 체크- 중복방지, 비밀번호해시, 디비저장, 토큰, 포지션(선택값)
#find_one사용 : 역할 : 찾는거
async def register(username:str, email:str, password:str, position:str|None = None) -> str:
    db = get_database()
    existing_user = await db["users"].find_one({"email":email})

    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    
    password_hash = hash_password(password)
    now = datetime.now(timezone.utc)
    result = await db["users"].insert_one({"username":username, "email":email, "password_hash":password_hash, 
    "role":"candidate", "is_active":True, "created_at": now, "updated_at":now,
    "last_login":None, "position":position, "refresh_token":None,})
    user_id = str(result.inserted_id)    
    token = create_access_token({"sub":user_id})
    return token

#로그인
#사용자 찾고 비밀번호 확인- 이메일/비번 오류, 사용자 없을 시 에러발생, 토큰
async def login(email:str, password:str) -> str:
    db = get_database()
    user = await db["users"].find_one({"email":email})

    if not user:  # 사용자 존재 여부 확인 (없으면 비밀번호 검증 자체가 불필요)
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")
    if not user["is_active"]:  # 비활성화 계정 차단 (비밀번호가 맞아도 로그인 불가)
        raise HTTPException(status_code=403, detail="비활성화된 계정입니다.")
    if not verify_password(password, user["password_hash"]):  # 비밀번호 검증 (활성 계정에 한해서만 수행)
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")
    
    user_id = str(user["_id"])
    await db["users"].update_one({"_id":ObjectId(user_id)}, {"$set": {"last_login": datetime.now(timezone.utc)}})
    token = create_access_token({"sub":user_id})
    return token
    

#로그아웃 : 리프레시토큰을 none으로
#update_one사용 : 역할 : 수정하기
async def logout(user_id:str) -> dict:
    db = get_database()
    await db["users"].update_one({"_id":ObjectId(user_id)},{"$set":{"refresh_token":None}})

    return {"message":"로그아웃되었습니다."}

#내 정보 조회
#db에서 사용자 찾아서 반환
async def get_me(user_id:str) -> UserResponse:
    db = get_database()
    user = await db["users"].find_one({"_id":ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    return UserResponse.model_validate(user)

#프로필수정(이름, 비밀번호 변경)
async def update_me(user_id:str, username: str, current_password : str | None = None, new_password: str | None = None) -> UserResponse:
    db = get_database()
    user = await db["users"].find_one({"_id":ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    #기본필드(이름수정)
    fields = { "username" : username, "updated_at" : datetime.now(timezone.utc)}

    #비밀번호는 수정 시 검증
    if new_password:
        if not current_password:
            raise HTTPException(status_code=400, detail="현재 비밀번호를 입력해주세요.")
        if not verify_password(current_password, user["password_hash"]):
            raise HTTPException(status_code=400, detail="현재 비밀번호가 일치하지 않습니다.")
        fields["password_hash"] = hash_password(new_password)
        
    await db["users"].update_one({"_id":ObjectId(user_id)}, {"$set":fields})

    return await get_me(user_id)

#회원탈퇴
async def delete_me(user_id:str) -> dict:
    db = get_database()

    await db["users"].delete_one({"_id":ObjectId(user_id)})

    return {"message":"회원탈퇴가 완료되었습니다."}
