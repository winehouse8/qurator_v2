from motor.motor_asyncio import AsyncIOMotorClient
from datetime import timedelta
from cardnews.core.settings import get_settings

class Mongo:
    client: AsyncIOMotorClient = None
    db = None
    api_keys = None
    logs_meta = None
    logs_body = None

mongo = Mongo()

async def connect_to_mongo():
    s = get_settings()
    mongo.client = AsyncIOMotorClient(s.mongo_uri)
    mongo.db = mongo.client["cardnews"]
    mongo.api_keys = mongo.db["api_keys"]
    mongo.logs_meta = mongo.db["logs_meta"]
    mongo.logs_body = mongo.db["logs_body"]

    # 인덱스 – APIKey prefix & TTL(30일)
    await mongo.api_keys.create_index("prefix", unique=True)
    await mongo.logs_meta.create_index(
        [("api_key_prefix", 1), ("ts", -1)]
    )
    await mongo.logs_meta.create_index(
        "ts",
        expireAfterSeconds=int(timedelta(days=30).total_seconds()),
    )

async def close_mongo():
    mongo.client.close()
