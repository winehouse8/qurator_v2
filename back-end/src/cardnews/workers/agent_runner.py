# agent_runner.py – 리팩토링 버전
"""Card‑news generator powered by Google ADK + proxy 스크래핑.

변경 사항
-----------
1.  Agent instruction 문자열을 ``instructions.py`` 에 분리.
2.  분기 없는 카드뉴스 제작 파이프라인:
      Google 검색 ➜ FILTER_AGENT ➜ 본문 크롤링 ➜ TEXT_MAKER_AGENT
      ➜ IMG_KEYWORD_AGENT ➜ 이미지 URL 보강 ➜ 최종 JSON 반환.

   * layout 판단: 두 번째 장부터 'sub_title' 존재 여부에 따라
     category = "with_sub_title" / "no_sub_title" 로 설정.
"""
from __future__ import annotations

import asyncio
import json
import sys
import urllib.parse
from typing import List, Dict

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.events import Event, EventActions

from cardnews.scraping.proxy_client import ProxyRotationClient
from cardnews.scraping.parsers import (
    get_parsed_google_search_page,
    get_parsed_text_page,
    get_parsed_google_img_search_page,
)
from cardnews.scraping.utils import safe_parse_urls, clean_urls

from cardnews.workers.instructions import (
    FILTER_INSTRUCTION,
    TEXT_MAKER_INSTRUCTION,
    IMG_KEYWORD_INSTRUCTION,
)

# ---------------------------------------------------------------------------
# 공통 async 툴
# ---------------------------------------------------------------------------
async def search_google(client, keyword: str, max_results: int = 10, date_range: str | None = None) -> List[Dict[str, str]]:
    """Google 검색 결과 파싱."""
    url = f"https://www.google.com/search?q={keyword}&num={max_results}"
    if date_range:
        url += f"&tbs=qdr:{date_range}"
    html = await client.fetch(url)
    return get_parsed_google_search_page(html)


async def fetch_page_text(client, url: str) -> str:
    html = await client.fetch(url)
    return get_parsed_text_page(html)


_IMG_SEARCH_BASE = (
    "https://www.google.com/search"
    "?tbm=isch&tbs=itp:photo,isz:lt,islt:vga&ijn=0&q={q}"
)


async def search_google_images(
    client: ProxyRotationClient,
    keyword: str,
    top_k: int = 20,
) -> List[Dict[str, str]]:
    url = _IMG_SEARCH_BASE.format(q=urllib.parse.quote(keyword))
    html = await client.fetch(url)
    items = get_parsed_google_img_search_page(html)
    return items[:top_k]


async def parallel_fetch_texts(
    client: ProxyRotationClient,
    urls: List[str],
    max_concurrency: int = 5,
) -> str:
    sem = asyncio.Semaphore(max_concurrency)

    async def _worker(idx: int, url: str) -> str:
        async with sem:
            try:
                text = await fetch_page_text(client, url)
                text = text[:20_000]
                return (
                    f"---{idx+1}번째 페이지---\n{text}\n--------------------------------\n"
                )
            except Exception as e:
                print(f"⚠️  [{idx + 1}] {url} 실패: {e}")
                return ""

    tasks = [_worker(i, u) for i, u in enumerate(urls)]
    chunks = await asyncio.gather(*tasks)
    return "".join(chunks)

# ---------------------------------------------------------------------------
# Agent 정의
# ---------------------------------------------------------------------------
MODEL_LOW = "openai/gpt-4.1-nano"
MODEL_MID = "openai/gpt-4.1-mini"
MODEL_HIGH = "openai/o4-mini"

FILTER_AGENT = Agent(
    name="filter_agent",
    model=LiteLlm(model=MODEL_HIGH),
    instruction=FILTER_INSTRUCTION,
)

TEXT_MAKER_AGENT = Agent(
    name="text_maker_agent",
    model=LiteLlm(model=MODEL_HIGH),
    instruction=TEXT_MAKER_INSTRUCTION,
)

IMG_KEYWORD_AGENT = Agent(
    name="img_keyword_agent",
    model=LiteLlm(model=MODEL_HIGH),
    instruction=IMG_KEYWORD_INSTRUCTION,
)

# ---------------------------------------------------------------------------
# Runner helper
# ---------------------------------------------------------------------------
async def _run_agent(runner: Runner, user_msg: str) -> str:
    content = types.Content(role="user", parts=[types.Part(text=user_msg)])
    async for event in runner.run_async(user_id="user", session_id="sess", new_message=content):
        if event.is_final_response():
            return event.content.parts[0].text if event.content and event.content.parts else ""
    raise RuntimeError("Agent did not return final response")

# ---------------------------------------------------------------------------
# 메인 워크플로
# ---------------------------------------------------------------------------
async def generate_cardnews(client, keyword: str, date_range: str | None = None) -> str:
    if date_range == "None":
        date_range = None

    # 세션 초기화
    service = InMemorySessionService()
    service.create_session(app_name="app", user_id="user", session_id="sess")
    session = service.get_session(app_name="app", user_id="user", session_id="sess")

    # keyword 주입
    service.append_event(
        session,
        Event(
            invocation_id="set_state",
            author="system",
            actions=EventActions(state_delta={"keyword": keyword}),
        ),
    )

    # 1️⃣ Google 검색
    try:
        search_results = await search_google(client, keyword, 15, date_range)
    except:
        return json.dumps([{}])
    print("====== search_results ======")
    print("count:", len(search_results))

    service.append_event(
        session,
        Event(
            invocation_id="set_state",
            author="system",
            actions=EventActions(state_delta={"search_results": search_results}),
        ),
    )

    # 2️⃣ URL 필터링
    runner_flt = Runner(agent=FILTER_AGENT, app_name="app", session_service=service)
    selected_json: str = await _run_agent(runner_flt, "filter")
    selected_url_list = clean_urls(safe_parse_urls(selected_json))

    print("===== 선택된 URL =====")
    print(selected_url_list)

    if len(selected_url_list)==0:
        return json.dumps([{}])

    # 3️⃣ 본문 크롤링
    page_texts = await parallel_fetch_texts(client, selected_url_list, 5)
    service.append_event(
        session,
        Event(
            invocation_id="set_state",
            author="system",
            actions=EventActions(state_delta={"page_texts": page_texts}),
        ),
    )

    # 4️⃣ 카드뉴스 초안 생성
    runner_txt = Runner(agent=TEXT_MAKER_AGENT, app_name="app", session_service=service)
    cards_json_str: str = await _run_agent(runner_txt, "generate")

    # cards_json 세션 저장 (img‑keyword 단계에서 사용)
    service.append_event(
        session,
        Event(
            invocation_id="set_state",
            author="system",
            actions=EventActions(state_delta={"cards_json": cards_json_str}),
        ),
    )

    # 5️⃣ img_keyword 보강
    runner_imgkw = Runner(agent=IMG_KEYWORD_AGENT, app_name="app", session_service=service)
    cards_with_kw_str: str = await _run_agent(runner_imgkw, "add_img_kw")

    try:
        cards_data = json.loads(cards_with_kw_str)
        pages: List[Dict] = cards_data["cards"] if isinstance(cards_data, dict) else cards_data
    except Exception as e:
        raise ValueError(f"IMG_KEYWORD_AGENT returned invalid JSON: {e}")

    # 6️⃣ 이미지 URL 크롤링 병합
    async def _enrich_page(page: Dict) -> Dict:
        if "img_keyword" not in page:
            return page
        kw = page["img_keyword"]
        img_res = await search_google_images(client, kw, 20)
        page["img_urls"] = [r["img_url"] for r in img_res]
        page["ref_urls"] = [r["ref_urls"] for r in img_res]
        page["img_desc"] = [r["img_desc"] for r in img_res]
        return page

    sem = asyncio.Semaphore(5)

    async def _wrap(p):
        async with sem:
            return await _enrich_page(p)
    try:
        pages = await asyncio.gather(*[_wrap(p) for p in pages])
    except:
        return json.dumps([{}])

    # 7️⃣ category 결정
    layout = (
        "with_sub_title" if any("sub_title" in card for card in pages[1:]) else "no_sub_title"
    )

    res_json = {
        "category": layout,
        "cards": pages,
        "desc": "default descriptions",
    }

    # 디버그 출력
    for i, card in enumerate(pages, 1):
        print(f"[{i}] card")
        for k in ("title", "sub_title", "body", "img_keyword"):
            if k in card:
                print(f"{k}: {card[k]}")
        print("--------------------------------")

    return json.dumps(res_json, ensure_ascii=False)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent_runner.py <keyword> [date_range]")
        sys.exit(1)

    kw = sys.argv[1]
    date_range_arg = sys.argv[2] if len(sys.argv) > 2 else None  # d, w, m, y, None

    proxy_client = ProxyRotationClient()
    output_json_str = asyncio.run(generate_cardnews(proxy_client, kw, date_range_arg))

    # Save to file
    with open("json_output.txt", "w", encoding="utf-8") as fp:
        fp.write(output_json_str)

    # Pretty‑print to console
    output_json = json.loads(output_json_str)
    import pdb; pdb.set_trace()
