from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.spotify import search_track

router = APIRouter()

@router.get("/")
async def search_song(title: str = Query(...), artist: str = Query(...)):
    try:
        spotify_url = await search_track(title, artist)
        youtube_url = (
            "https://www.youtube.com/results?search_query="
            + f"{title} {artist}"
        )
        return {"spotify_url": spotify_url, "youtube_url": youtube_url}
    except Exception as e:
        print("❌ 검색 중 오류:", e)
        raise HTTPException(500, "검색 실패")