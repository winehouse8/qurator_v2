import hmac, hashlib
from fastapi import Depends, Header, HTTPException, status
from cardnews.core.db import mongo
from cardnews.core.settings import get_settings

def hash_key(raw: str) -> str:
    secret = get_settings().api_hash_secret.encode()
    return hmac.new(secret, raw.encode(), hashlib.sha256).hexdigest()

async def verify_api_key(x_api_key: str = Header(...)):
    """FastAPI dependency — 401 if invalid"""
    pref = x_api_key[:8]
    doc = await mongo.api_keys.find_one({"prefix": pref, "active": True})
    if not doc or not hmac.compare_digest(doc["hash"], hash_key(x_api_key)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid API Key")
    return pref  # 나중에 로그용 반환
