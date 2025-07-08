# app/routers/oauth.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
import os
import jwt
import requests
from supabase import create_client, Client  # Supabase 클라이언트

from ..auth.oauth_client import oauth

router = APIRouter()

# 🐾 Supabase 클라이언트 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않았긔!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="code 파라미터가 없긔!")

    # 구글 토큰 발급
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
            "grant_type": "authorization_code",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    access_token = token_resp.json().get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="구글 토큰 발급 실패긔!")

    # 사용자 정보 조회
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    ).json()
    email = user_info.get("email")
    user_id = user_info.get("sub")
    if not email or not user_id:
        raise HTTPException(status_code=400, detail="사용자 정보를 가져올 수 없긔😢")

    try:
        supabase.table("users")\
                 .upsert({"user_id": user_id, "email": email})\
                 .execute()
    except Exception as e:
        print(f"⚠️ Supabase 유저 업서트 실패: {e}")

    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET이 설정되지 않았긔!")
    jwt_token = jwt.encode({"email": email, "user_id": user_id}, secret, algorithm="HS256")

    frontend = os.getenv("FRONTEND_URL")
    if not frontend:
        raise HTTPException(status_code=500, detail="FRONTEND_URL이 설정되지 않았긔!")
    redirect_to = f"{frontend}?token={jwt_token}&email={email}&user_id={user_id}"
    return RedirectResponse(redirect_to)