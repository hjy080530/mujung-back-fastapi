# app/routers/oauth.py
from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
import os
import jwt
import requests

from ..auth.oauth_client import oauth

router = APIRouter()

@router.get("/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request):

    code = request.query_params.get("code")

    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')

    print(code)

    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    token = token_response.json().get("access_token")

    headers = {
        "Authorization": f"Bearer {token}"
    }
    user_response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)

    user_info = user_response.json()

    email = user_info.get("email")
    user_id = user_info.get("sub")

    print("아이디 : " + user_id)
    print("이메일 : " + email)

    if not email or not user_id:
        raise HTTPException(status_code=400, detail="사용자 정보를 가져올 수 없습니다.😢")

    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise HTTPException(
            status_code=500,
            detail="서버 환경변수 JWT_SECRET이 설정되지 않았긔!"
        )
    jwt_token = jwt.encode(
        {"email": email, "user_id": user_id},
        secret,
        algorithm="HS256"
    )

    frontend_url = (
        f"{os.getenv('FRONTEND_URL')}"  # .env 에 e.g. https://mujung-three.vercel.app
        f"?token={jwt_token}&email={email}&user_id={user_id}"
    )
    return RedirectResponse(frontend_url)