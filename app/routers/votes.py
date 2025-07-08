from urllib import request

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.votes import has_already_voted, insert_vote

router = APIRouter()

class VoteIn(BaseModel):
    link_id: str
    user_id: str

@router.post("", status_code=201)
def vote(vote: VoteIn):
    raw =request.body()
    print("📦 Raw request body:", raw)
    return {"debug": raw}
    # 1. 중복 투표 검사
    if has_already_voted(vote.user_id, vote.link_id):
        raise HTTPException(status_code=409, detail="이미 투표했습니다")

    # 2. 투표 삽입
    response = insert_vote(vote.user_id, vote.link_id)

    if not response.data:
        raise HTTPException(status_code=500, detail="투표 저장 실패")

    return { "message": "투표 완료!" }