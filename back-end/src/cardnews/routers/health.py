from fastapi import APIRouter
from cardnews.core.db import mongo
import asyncio

router = APIRouter()

@router.get("/health")
async def health():
    try:
        await mongo.client.admin.command({"ping": 1})
        mongo_ok = True
    except Exception:
        mongo_ok = False

    # proxy client 객체 존재 여부만 확인
    proxy_ok = hasattr(mongo, "client")

    return {
        "mongo": "ok" if mongo_ok else "fail",
        "proxy": "ok" if proxy_ok else "fail",
    }
