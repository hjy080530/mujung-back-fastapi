from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ..services.supabase import supabase
from ..services.spotify import get_track_info

router = APIRouter()

class SongIn(BaseModel):
    link: str


@router.post("/", status_code=201)
async def create_song(song: SongIn):
    info = await get_track_info(song.link)

    # 먼저 Supabase에 upsert (실패 없이 저장되게)
    supabase.table("spotify_information").upsert({
        "link_id": info.link_id,
        "link": song.link,
        "song_name": info.name,
        "song_artist": info.artist
    }).execute()

    # 그리고 중복 체크
    existing = supabase.table("spotify_information")\
        .select("*").eq("link_id", info.link_id).execute()

    if existing.data and len(existing.data) > 1:
        # 실제로 중복된 데이터가 여러 개라면 예외 발생
        raise HTTPException(status_code=409, detail="이미 등록된 곡입니다.")

    # 처음 추가된 경우에는 그대로 응답
    return existing.data[0]

@router.get("/")
async def get_songs():
    result = supabase.table("spotify_information") \
        .select("*").order("link_id", desc=True).execute()

    # result는 APIResponse 객체고, .data 속성만 있는 경우가 많음
    if not result.data:
        raise HTTPException(404, "곡이 없습니다.")

    return result.dat