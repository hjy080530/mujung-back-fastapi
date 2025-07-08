from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.votes import has_already_voted, insert_vote
from app.services.supabase import supabase

router = APIRouter()

class VoteIn(BaseModel):
    link_id: str
    email: EmailStr

@router.post("/", status_code=201)
def vote(vote: VoteIn):
    # 1. 이메일 도메인 체크
    if not vote.email.endswith("@bssm.hs.kr"):
        raise HTTPException(status_code=403, detail="bssm 이메일만 허용됩니다")

    # 2. Supabase에서 user 조회
    user_result = supabase.table("users")\
        .select("user_id")\
        .eq("email", vote.email)\
        .execute()

    if not user_result.data:
        raise HTTPException(status_code=404, detail="해당 이메일의 유저가 없습니다")

    user_id = user_result.data[0]["user_id"]

    # 3. 중복 투표 검사
    if has_already_voted(user_id, vote.link_id):
        raise HTTPException(status_code=409, detail="이미 투표했습니다")

    # 4. 투표 삽입
    response = insert_vote(user_id, vote.link_id)

    if not response.data:
        raise HTTPException(status_code=500, detail="투표 저장 실패")

    return { "message": "투표 완료!" }