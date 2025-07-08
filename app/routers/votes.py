from supabase import create_client, Client
import os
from fastapi import HTTPException

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL 또는 SUPABASE_KEY 환경변수가 없습니다.😢")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def has_already_voted(user_id: str, link_id: str) -> bool:
    resp = supabase.table("votes")\
                   .select("id")\
                   .eq("user_id", user_id)\
                   .eq("link_id", link_id)\
                   .execute()
    return bool(resp.data)

def insert_vote(user_id: str, link_id: str):
    try:
        supabase.table("users")\
                 .upsert({"id": user_id})\
                 .execute()
    except Exception as e:
        print(f"⚠️ Supabase 유저 업서트 에러: {e}")

    try:
        result = supabase.table("votes")\
                         .insert({"user_id": user_id, "link_id": link_id})\
                         .execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"투표 저장 실패: {e}")

    return result