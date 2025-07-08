# app/routers/__init__.py
from .songs import router as songs
from .votes import router as votes
from .search import router as search
from .oauth import router as oauth

__all__ = ["songs", "votes", "search", "oauth"]