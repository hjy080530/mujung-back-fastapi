from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.spotify import search_track

router = APIRouter()

@router.get("/")
async def search_song(title: str = Query(...), artist: str = Query(...)):
    try:
        spotify_url = await search_track(title, artist)
        youtube_url = f"https://www.youtube.com/results?search_query={title}+{artist}"
        return {"spotify_url": spotify_url, "youtube_url": youtube_url}
    except ValueError as ve:
        print(f"❌ 검색 실패: title='{title}', artist='{artist}' → {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류 (search_song)")