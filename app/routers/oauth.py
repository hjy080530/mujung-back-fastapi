# app/routers/oauth.py
from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
import os
import jwt

from ..auth.oauth_client import oauth
router = APIRouter()

@router.get("/google")
async def google_login(request: Request):
    # 구글 로그인으로 리다이렉트할 URI 생성
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request):
    try:
        # 구글에서 인증 정보 받기
        token = await oauth.google.authorize_access_token(request)
        user_info = await oauth.google.parse_id_token(request, token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth 인증 실패: {e}")

    # 사용자 정보 추출
    email = user_info.get("email")
    user_id = user_info.get("sub")
    if not email or not user_id:
        raise HTTPException(status_code=400, detail="사용자 정보를 가져올 수 없습니다.")

    # JWT 생성
    jwt_token = jwt.encode(
        {"email": email, "user_id": user_id},
        os.getenv("JWT_SECRET"),
        algorithm="HS256"
    )

    # 프론트엔드로 리다이렉트 (토큰 전달)
    frontend_url = (
        "https://mujung-three.vercel.app/"
        f"?token={jwt_token}&email={email}&user_id={user_id}"
    )
    return RedirectResponse(frontend_url)
