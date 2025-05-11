# ProxyRotationClient.py

import os
import asyncio
import time
import yaml
from dotenv import load_dotenv
from camoufox.async_api import AsyncCamoufox
import sys

# UTF-8 출력을 강제
sys.stdout.reconfigure(encoding='utf-8')

# 환경 변수 로드
load_dotenv()
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")

# 설정 로드 (.yaml)
with open("config.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
PORTS = cfg.get("ports", [])
MIN_DELAY = cfg.get("min_delay", 10)           # 각 프록시당 최소 대기 시간 (초)
MAX_RETRIES = cfg.get("max_retries", 2)        # 실패 시 최대 재시도 횟수
USER_AGENT = cfg.get("user_agent", None)       # Optional: 사용자 에이전트 설정

class ProxyRotationClient:
    def __init__(self):
        # 프록시 리스트 생성
        self.proxies = [
            {
                "server": f"http://{PROXY_HOST}:{port}",
                "username": PROXY_USER,
                "password": PROXY_PASS,
            }
            for port in PORTS
        ]
        self.n = len(self.proxies)
        self._idx = 0
        # 마지막 요청 시간 기록 (proxy_index -> timestamp)
        self.last_request_time = {i: 0 for i in range(self.n)}

    def _next_index(self) -> int:
        # 순환형 인덱스
        idx = self._idx % self.n
        self._idx += 1
        return idx

    async def fetch(self, url: str) -> str:
        attempts = 0
        while attempts <= MAX_RETRIES:
            idx = self._next_index()
            proxy_conf = self.proxies[idx]

            # 최소 지연 시간 확보
            elapsed = time.time() - self.last_request_time[idx]
            if elapsed < MIN_DELAY:
                await asyncio.sleep(MIN_DELAY - elapsed)

            try:
                async with AsyncCamoufox(
                    headless=True,
                    proxy=proxy_conf,
                    geoip=True,
                    os=["windows", "macos", "linux"],
                    locale=["en-US", "ko-KR"],
                    block_images=True,
                    disable_coop=True,
                    i_know_what_im_doing=True
                ) as browser:
                    page = await browser.new_page()
                    await page.goto(url, timeout=60_000, wait_until="networkidle")
                    html = await page.content()
                # 요청 성공 시 시간 기록 후 반환
                self.last_request_time[idx] = time.time()
                if "unusual traffic from your computer network" in html:
                    raise RuntimeError("봇 탐지됨")
                return html

            except Exception as e:
                attempts += 1
                # 재시도 허용 범위 내라면 다음 프록시로 전환
                if attempts <= MAX_RETRIES:
                    continue
                else:
                    raise RuntimeError(f"Failed to fetch after {MAX_RETRIES} retries: {e}")

async def main():
    import argparse

    #URL= "https://www.google.com/search?q=야탑 황금어장 횟집&tbm=isch&tbs=itp:photo,isz:lt,islt:qsvga"
    URL= "https://www.google.com/search?sca_esv=7c2ca09b3e09a761&sxsrf=AHTn8zqAYh0s10GdX8PyjYadVv-t_cVqHg:1746523768156&q=%EC%A2%85%EB%A1%9C%EB%8F%84%EB%8B%B4&udm=2&fbs=ABzOT_CZsxZeNKUEEOfuRMhc2yCI6hbTw9MNVwGCzBkHjFwaK321z773wCjxZUmvDroqphlIJR493mMxNbRCE7CsjxN0oXAvyvr41R_LOusV8UDJkkCumF09-rtz-NGps7Hlue5HqKPjWQVaHZZSp-ifHZI4M2M4YtJekPMX1Wdw5sjWWV8fZUEKOibQIb93aEbs0y4inum-5xy0FbQcMODfm87E303SxdmowcXHUTDN8ln4LLJYNM8&sa=X&sqi=2&ved=2ahUKEwi3x6uGxI6NAxXNe_UHHQf0GuEQtKgLegQICRAB&biw=1271&bih=761&dpr=1.1"

    client = ProxyRotationClient()
    html = await client.fetch(URL)
    # 파일에 저장
    with open("result_html.txt", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved HTML to html.txt")

if __name__ == "__main__":
    asyncio.run(main())
