# create_test_apikey.py
import os, hmac, hashlib, secrets, asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from dotenv import load_dotenv
load_dotenv()

API_HASH_SECRET = os.environ["API_HASH_SECRET"].encode()
MONGO_URI       = os.environ["MONGO_URI"]

def hash_key(raw: str) -> str:
    return hmac.new(API_HASH_SECRET, raw.encode(), hashlib.sha256).hexdigest()

async def main():
    # 1) 무작위 Key 한 개 생성 (URL-safe 32바이트 ≈ 43글자)
    raw_key = secrets.token_urlsafe(32)              # 👉 클라이언트에게 줄 값
    doc = {
        "prefix": raw_key[:8],                       # 색인용 접두어
        "hash":   hash_key(raw_key),                 # HMAC-SHA-256
        "company": "TestCorp",
        "active": True
    }

    # 2) Mongo 삽입
    cli = AsyncIOMotorClient(MONGO_URI)
    await cli.cardnews.api_keys.insert_one(doc)
    cli.close()

    print("✅ 발급된 테스트 API Key:\n", raw_key)

if __name__ == "__main__":
    asyncio.run(main())
