from app.database import get_database
from app.domain.user.models import UserDocument
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException
from datetime import datetime


#회원가입
#이메일(아이디) 체크-에러써야겠네 여기서 중복방지, 비밀번호해시, 디비저장, 토큰
#find_one사용 : 역할 : 찾는거
async def register(username, email, password, position):
    db = get_database()
    existing_user = await db["users"].find_one({"email":email})

    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    
    password_hash = hash_password(password)
    await db["users"].insert_one({"username":username, "email":email, "password_hash":password_hash, 
    "role":"candidate", "is_active":True, "created_at": datetime.now(), "updated_at":datetime.now(),
    "last_login":None, "position":position, "refresh_token":None,})
    token = create_access_token({"sub":email})
    return token

#로그인
#사용자 찾고 비밀번호 확인- 여기서도 이메일이랑 비번 틀리면, 없으면 에러발생하는거 작성, 토큰발급하고 반환
async def login(email, password):
    db = get_database()
    user = await db["users"].find_one({"email":email})

    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 잘못되었습니다.")
    
    token = create_access_token({"sub":email})
    return token
    

#로그아웃 : 리프레시토큰을 none으로
#update_one사용 : 역할 : 수정하기
async def logout(email):
    db = get_database()
    await db["users"].update_one({"email":email}),({"$set":{"refresh_token":None}})

    return {"message":"로그아웃되었습니다."}

#내 정보 조회
#db에서 나 찾아서 반환해주게
async def get_me(email):