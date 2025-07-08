import os
from typing import List
import httpx
from pydantic import BaseModel

class TrackInfo(BaseModel):
    link_id: str
    name: str
    artist: str

class SearchResult(BaseModel):
    track_id: str
    name: str
    artist: str

async def get_track_info(link: str) -> TrackInfo:
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"))
        )

        token = token_res.json()["access_token"]

        track_id = link.split("/")[-1].split("?")[0]

        track_res = await client.get(
            f"https://api.spotify.com/v1/tracks/{track_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        track_data = track_res.json()
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