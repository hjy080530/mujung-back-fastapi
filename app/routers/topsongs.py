# app/routers/topsongs.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from collections import Counter
import os
from supabase import create_client, Client

from app.services.spotify import get_track_info, TrackInfo
from pydantic import BaseModel

class TopSong(BaseModel):
    link_id: str
    name: Optional[str]
    artist: Optional[str]
    votes: int

router = APIRouter()

# Supabase 클라이언트 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL 또는 SUPABASE_KEY 환경변수가 없습니다.😢")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("", response_model=List[TopSong])
async def top_songs():
    try:
        resp = supabase.table("votes").select("link_id").execute()
    except Exception:
        raise HTTPException(status_code=500, detail="투표 조회 실패😿")

    votes_data = resp.data
    if not isinstance(votes_data, list):
        raise HTTPException(status_code=500, detail="투표 조회 데이터 형식 오류😿")

    counts = Counter(item.get("link_id") for item in votes_data if item.get("link_id"))
    top5 = counts.most_common(5)
    results: List[TopSong] = []

    for link_id, cnt in top5:
        name: Optional[str] = None
        artist: Optional[str] = None
        try:
            info: TrackInfo = await get_track_info(f"https://open.spotify.com/track/{link_id}")
            name = info.name
            artist = info.artist
        except HTTPException:
            pass

        results.append(TopSong(link_id=link_id, name=name, artist=artist, votes=cnt))

    return results

