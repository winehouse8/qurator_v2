from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware


import uvicorn, asyncio
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.gzip import GZipMiddleware
from cardnews.core.db import connect_to_mongo, close_mongo
from cardnews.routers.cardnews import router
from cardnews.services.cardnews_service import client
from cardnews.scraping.proxy_client import ProxyRotationClient
from cardnews.core.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="CardNews MVP",
    version="0.2.0",
    default_response_class=ORJSONResponse
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ⭐ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⭐ 라우터
from cardnews.routers.cardnews import router as card_router
from cardnews.routers.health import router as health_router
app.include_router(card_router)
app.include_router(health_router)

# ⭐ Prometheus
Instrumentator().instrument(app).expose(app)

# ⭐ SlowAPI 전역 핸들러 (cardnews.py에도 세팅했지만, 전역 예외처리 안전망)
limiter = Limiter(key_func=get_remote_address,
                  default_limits=[f"{settings.rate_limit_per_min}/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    # ProxyRotationClient 싱글턴 준비
    import importlib
    svc = importlib.import_module("cardnews.services.cardnews_service")
    svc.client = ProxyRotationClient()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,           # ↔ 개발 중 only
        workers=1               # 멀티-워커면 메모리 주의
    )
