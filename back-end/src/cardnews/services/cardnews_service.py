import asyncio
import gzip
import json
from datetime import datetime

import bson

from cardnews.core.db import mongo
from cardnews.scraping.proxy_client import ProxyRotationClient
from cardnews.workers.agent_runner import generate_cardnews

# ProxyRotationClient 싱글턴 (startup 이벤트에서 주입됩니다)
client: ProxyRotationClient | None = None


async def _log_async(prefix: str, query: str, body: bytes) -> None:
    """Card‑news 결과를 MongoDB에 gzip 압축해 비동기 저장."""
    meta = {
        "ts": datetime.utcnow(),
        "api_key_prefix": prefix,
        "query": query,
        "body_size": len(body),
    }

    # 본문 컬렉션에 먼저 저장하고 ObjectId 를 메타와 연결
    body_id = (
        await mongo.logs_body.insert_one({"body_gzip": bson.Binary(gzip.compress(body))})
    ).inserted_id
    meta["body_id"] = body_id
    print("--------------------------------")
    print("save meta")
    print(meta)
    print("--------------------------------")
    try:
        await mongo.logs_meta.insert_one(meta)
    except Exception as e:
        print(f"Error inserting log meta: {e}")


async def generate_and_log(
    query: str,
    date_range: str | None,
    api_key_prefix: str,
) -> dict:
    """카드뉴스 생성 후 로그까지 남기는 메인 엔트리 포인트.

    * `query`        – 사용자가 요청한 키워드
    * `date_range`   – Google 검색 기간 필터 (d, w, m, m3, y, None)
    * `api_key_prefix` – 인증된 API 키 접두어(로그용)
    """
    if client is None:
        raise RuntimeError("Proxy client not initialized (startup 이벤트 확인)")

    # ① 카드뉴스 생성 -------------------------------------------------------
    json_str = await generate_cardnews(client, query, date_range)
    raw_bytes = json_str.encode()

    # ② 비동기 로깅 ---------------------------------------------------------
    # 메인 이벤트 루프에 태스크를 붙여두면 Starlette BackgroundTask 의 루프 충돌 문제 해결
    asyncio.create_task(_log_async(api_key_prefix, query, raw_bytes))

    # ③ 결과 반환 (dict)
    return json.loads(json_str)
