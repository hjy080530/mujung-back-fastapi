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

    supabase.table("spotify_information").upsert({
        "link_id": info.link_id,
        "link": song.link,
        "song_name": info.name,
        "song_artist": info.artist
    }).execute()

    existing = supabase.table("spotify_information")\
        .select("*").eq("link_id", info.link_id).execute()

    if existing.data and len(existing.data) > 1:
        raise HTTPException(status_code=409, detail="이미 등록된 곡입니다.")

    return existing.data[0]

@router.get("/")
async def get_songs():
    result = supabase.table("spotify_information") \
        .select("*").order("link_id", desc=True).execute()

    if not result.data:
        raise HTTPException(404, "곡이 없습니다.")

    return result.data