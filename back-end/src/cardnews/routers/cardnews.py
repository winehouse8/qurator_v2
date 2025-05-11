# src/cardnews/routers/cardnews.py
from enum import Enum

from fastapi import APIRouter, Depends, Request
from fastapi.responses import ORJSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from cardnews.core.security import verify_api_key
from cardnews.core.settings import get_settings
from cardnews.services.cardnews_service import generate_and_log

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_min}/minute"],
)

router = APIRouter()


class RangeEnum(str, Enum):
    d = "d"
    w = "w"
    m = "m"
    m3 = "m3"
    y = "y"
    none = "None"  # 파라미터 미전송 시 기본값


@router.get("/generate", response_class=ORJSONResponse)
@limiter.limit(f"{settings.rate_limit_per_min}/minute")
async def generate_cardnews_endpoint(
    request: Request,                               # SlowAPI용 필수
    q: str,                                         # 검색 키워드
    range_: RangeEnum = RangeEnum.none,             # ← 복원 ✅
    api_key_prefix: str = Depends(verify_api_key),  # API-Key 검증
):
    """
    카드뉴스 생성 엔드포인트  
    - **q**      : 검색 키워드  
    - **range**  : d, w, m, m3, y 또는 None  
    """
    # Enum → 실제 값(None / 'd' …)
    date_range = None if range_ == RangeEnum.none else range_.value

    # 카드뉴스 생성 & 로그
    data = await generate_and_log(q, date_range, api_key_prefix)
    return data
