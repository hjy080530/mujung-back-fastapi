from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()  # .env 로드

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET_KEY", "fallback-secret"),
    same_site="none",
    https_only=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mujung-three.vercel.app"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True
)

from app.routers.songs import router as songs_router
from app.routers.votes import router as votes_router
from app.routers.search import router as search_router
from app.routers.oauth import router as oauth_router
from app.routers.topsongs import router as topsongs_router
from app.routers.spotifytop import router as spotifytops_router

app.include_router(songs_router, prefix="/songs")
app.include_router(votes_router, prefix="/votes")
app.include_router(search_router, prefix="/search")
app.include_router(oauth_router, prefix="/oauth")
app.include_router(topsongs_router, prefix="/topsongs")
app.include_router(spotifytops_router, prefix="/spotify")