# app/routers/votes.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.services.votes_service import has_already_voted, insert_vote

router = APIRouter()

class VoteIn(BaseModel):
    link_id: str
    user_id: str

@router.post("/", status_code=201)
async def vote(vote: VoteIn, request: Request):
    raw = await request.body()
    print("📦 Raw request body:", raw)

    if has_already_voted(vote.user_id, vote.link_id):
        raise HTTPException(status_code=409, detail="이미 투표했습니다😼")

    result = insert_vote(vote.user_id, vote.link_id)
    if not getattr(result, "data", None):
        raise HTTPException(status_code=500, detail="투표 저장 실패😿")

    return { "message": "투표 완료했음" }