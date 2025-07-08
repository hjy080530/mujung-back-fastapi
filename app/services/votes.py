from pydantic import BaseModel

from app.services.supabase import supabase
class VoteCreate(BaseModel):
    link_id: str
    user_id: str
def has_already_voted(user_id: str, link_id: str) -> bool:
    result = supabase.table("votes")\
        .select("user_id")\
        .eq("user_id", user_id)\
        .eq("link_id", link_id)\
        .execute()
    return bool(result.data)

def insert_vote(user_id: str, link_id: str):
    return supabase.table("votes").insert({
        "user_id": user_id,
        "link_id": link_id
    }).execute()