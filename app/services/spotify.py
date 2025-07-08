import os
from typing import List
import httpx
from fastapi import HTTPException
from pydantic import BaseModel

class TrackInfo(BaseModel):
    link_id: str
    name: str
    artist: str

class SearchResult(BaseModel):
    track_id: str
    name: str
    artist: str

def extract_track_id(link: str) -> str:
    return link.split("/")[-1].split("?")[0]
async def get_track_info(link: str) -> TrackInfo:
    track_id = extract_track_id(link)

    # 1. Access Token 직접 요청
    token_res = await httpx.AsyncClient().post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"))
    )
    token = token_res.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        track_data = res.json()

        print("✅ SPOTIFY LINK:", link)
        print("🔍 RESPONSE STATUS:", res.status_code)
        print("📦 RESPONSE JSON:", track_data)

        if res.status_code != 200 or "name" not in track_data:
            raise HTTPException(status_code=500, detail="Spotify 트랙 정보 오류")

        return TrackInfo(
            link_id=track_id,
            name=track_data["name"],
            artist=track_data["artists"][0]["name"]
        )

async def search_track(title: str, artist: str) -> str:
    query = f"{title} {artist}"

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"))
        )
        token = token_res.json()["access_token"]

        res = await client.get(
            "https://api.spotify.com/v1/search",
            params={"q": query, "type": "track", "limit": 5},
            headers={"Authorization": f"Bearer {token}"}
        )

        data = res.json()
        items = data.get("tracks", {}).get("items", [])

        if not items:
            raise ValueError("검색 결과가 없습니다.")

        # 가장 첫 번째 검색 결과의 링크 반환
        return f"https://open.spotify.com/track/{items[0]['id']}"