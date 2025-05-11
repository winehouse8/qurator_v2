"""agent.py – Sequential Card-News Workflow (async-only, official ADK)
===================================================================
키워드 ➜ 분류 ➜ URL 필터 ➜ 카드뉴스 생성 3단계를 비동기 툴로 실행합니다.
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
from cardnews.scraping.parsers import get_parsed_google_search_page, get_parsed_text_page, get_parsed_google_img_search_page
from cardnews.scraping.utils import safe_parse_urls, clean_urls

# ---------------------------------------------------------------------------
# 공통 async 툴
# ---------------------------------------------------------------------------

async def search_google(client, keyword: str, max_results: int = 15, date_range:str=None) -> List[Dict[str, str]]:
    """Performs a Google search and returns parsed top-N results.

    Args:
        keyword: Search query string.
        max_results: Google num parameter.

    Returns:
        list[dict] with keys ``desc`` and ``url``.
    """
    
    url = f"https://www.google.com/search?q={keyword}&num={max_results}"
    if date_range:
        url+=f"&tbs=qdr:{date_range}"
    html = await client.fetch(url)
    return get_parsed_google_search_page(html)


async def fetch_page_text(client, url: str) -> str:
    """Scrapes a single page and returns visible main text."""
    html = await client.fetch(url)
    return get_parsed_text_page(html)

IMG_SEARCH_BASE = (
    "https://www.google.com/search"
    "?tbm=isch&tbs=itp:photo,isz:lt,islt:vga&ijn=0&q={q}"
)

async def search_google_images(
    client: ProxyRotationClient,
    keyword: str,
    top_k: int = 20,
) -> List[Dict[str, str]]:
    """
    img_keyword 로 Google 이미지 검색 → 상위 top_k 결과만 반환
    """
    url = IMG_SEARCH_BASE.format(q=urllib.parse.quote(keyword))
    html = await client.fetch(url)
    items = get_parsed_google_img_search_page(html)   # ✅ 이미 만들어둔 파서
    return items[:top_k]


async def parallel_fetch_texts(
    client: ProxyRotationClient,
    urls: List[str],
    max_concurrency: int = 5,
) -> str:
    """
    크롤링할 URL 목록을 병렬(동시 max_concurrency개)로 요청해
    각 페이지에서 추출한 텍스트를 하나의 문자열로 이어서 반환합니다.

    Args
    ----
    client           : 이미 생성·공유된 ProxyRotationClient 인스턴스
    urls             : 크롤링할 URL 목록
    max_concurrency  : 동시에 실행할 fetch 작업 수(기본 5)

    Returns
    -------
    str : `"---1번째 페이지---\\n...\\n--------------------------------\\n"`  
          형태로 이어붙인 결과
    """
    sem = asyncio.Semaphore(max_concurrency)

    async def _worker(idx: int, url: str) -> str:
        async with sem:                       # 동시 요청 개수 제한
            try:
                text = await fetch_page_text(client, url)
                text = text[:20_000]          # 너무 길면 컷
                return (
                    f"---{idx + 1}번째 페이지---\n"
                    f"{text}\n"
                    f"--------------------------------\n"
                )
            except Exception as e:
                print(f"⚠️ [{idx + 1}] {url} 실패: {e}")
                return ""

    # 코루틴을 한꺼번에 스케줄링
    tasks = [_worker(i, u) for i, u in enumerate(urls)]
    chunks = await asyncio.gather(*tasks)
    return "".join(chunks)

# ---------------------------------------------------------------------------
# Agent 정의
# ---------------------------------------------------------------------------

MODEL_LOW = "openai/gpt-4.1-nano"
MODEL_MID = "openai/gpt-4.1-mini"
MODEL_HIGH = "openai/o4-mini"

CLASSIFY_AGENT = Agent(
    name="classify_agent",
    model=LiteLlm(model=MODEL_LOW),
    instruction=(
        "사용자가 요청한 카드뉴스 주제 '{keyword}' 를 보고 카테고리를 정확히 장소,꿀팁,뉴스 중에 하나로 출력하세요. 이외의 단어는 출력하지 마세요.\n"
        "- 음식·맛집·카페·데이트코스·전시회·가게 ⇒ 장소\n"
        "- 사용법·팁·비법·노하우·정보 ⇒ 꿀팁'\n"
        "- 최신 뉴스 사건 ⇒ 뉴스'\n")
)

FILTER_AGENT = Agent(
    name="filter_agent",
    model=LiteLlm(model=MODEL_HIGH),
    instruction=(
        "{search_results} 이 text는 list[dict] 형태이며, dict의 key는 desc,url로 이루어져 있어. desc를 보고 광고·낚시 제외하고 검색어 사용자가 요청한 카드뉴스 주제 '{keyword}'와 관련성 높은 정보를 선택해 그에 해당하는 URL 최대 5개를 골라, url을 요소로 갖는 list로 출력하세요. 예를들면 ['www.asdds', 'www.asdasd'] 형태입니다. 꼭 그냥 하나의 list로만 출력하고, 다른 텍스트를 출력하지 마세요."),
)

RESTAURANT_MAKER = Agent(
    name="restaurant_maker",
    model=LiteLlm(model=MODEL_HIGH),
    instruction=(
        "아래 검색 결과를 바탕으로 '{keyword}'에 대한 카드뉴스 list(dict) 형식의 JSON(2~6장)만 출력하세요.\n"
        "- 첫 dict: title, img_keyword 를 key로 가지는 dict\n"
        "- 이후 dict: sub_title, body, img_keyword를 key로 가지는 dict\n"
        "title 은보통의 SNS 포스팅 제목처럼, 쉽고 직설적으로 흥미로운 표현을 써서 클릭을 유도하는 제목을 쓰는것이 좋습니다.\n"
        "sub_title에는 해당 장소 또는 상호 이름을 기본으로 적는데, 만약 일반적인 상호라면, 잠실~~떡볶이 처럼 지명을 상호 앞에 함께 적어 특정할 수 있도록 써야합니다. 만약  기본으로 적은 장소 또는 상호 이름 이외로 추가로 소제목으로 붙히면 좋은 정보가 있으면, 추가해도 됩니다."
        "body에는 해당 장소 또는 가게에 대한 간략한 장점,특징, 주요정보(주요메뉴,기간/시간 등)를 씁니다. 만약 검색 결과상 주요정보(주요메뉴,기간/시간 등)가 없으면 쓰지 않아도 되지만, 있다면 쓰는것이 좋습니다. 최대 100자 이내 (2~4문장)로 써야합니다. 꼭 최대 글자수를 채울 필요는 없지만, 독자들이 흥미로워할 내용이 많다면 길게, 아니라면 짧게 쓰고 넘어가는게 좋습니다."
        "img_keyword는 sub_title과 똑같이, 해당 장소/가게 이름으로 쓰면돼. 다만  title에 들어가는 img_keyword로는, 주제와 관련있으면서 후킹하도록 어떤 사진이 들어가면 좋을지 생각한뒤, 그 사진을 검색할 수 있는 검색어를 적어줘. 내용과 꼭 100% 일치하지 않더라도, 관련있으면서 구글 이미지 검색시 배경으로 쓸만한 사진이 나올만한 검색어를 써야합니다.\n"
        "꼭 필요한 경우가 아니면 한자는 쓰지마. 기본적으로는 한글로 쓰는게 좋아.\n"
        "다른 텍스트를 출력하지 말고 꼭 Json 형식의 출력만 하세요! 백틱json도 쓰지말고 그냥 대괄호,중괄호'[{' 로 바로 시작하도록.\n"
        "---참조할 검색 결과---\n"
        "{page_texts}")
)

TIPS_MAKER = Agent(
    name="tips_maker",
    model=LiteLlm(model=MODEL_HIGH),
    instruction=(
        "아래 검색 결과를 바탕으로 '{keyword}'에 대한 카드뉴스 list(dict) 형식의 JSON(2~6장)만 출력하세요.\n"
        "- 첫 dict: title, img_keyword 를 key로 가지는 dict\n"
        "- 이후 dict: sub_title, body, img_keyword를 key로 가지는 dict\n"
        "카드뉴스의 내용으로는 아래 참조할 검색 결과를 바탕으로 뻔한 사실이 아닌, 구체적이고 흥미로운 내용을 쓰는것이 중요합니다.\n"
        "title 은보통의 SNS 포스팅 제목처럼, 쉽고 직설적으로 흥미로운 표현을 써서 클릭을 유도하는 제목을 쓰는것이 좋습니다.\n"
        "sub_title은 최대 40자 이내, body는 최대 100자 이내 (2~4문장)로 써야합니다. 꼭 최대 글자수를 채울 필요는 없지만, 독자들이 흥미로워할 내용이 많다면 길게, 아니라면 짧게 쓰고 넘어가는게 좋습니다.\n"
        "img_keyword는 해당 페이지에 어울리는 이미지를 검색하기 위한 구글 검색어를 써야합니다. 특히 title쪽 img_keyword는 후킹한 사진을, 그 이후 img_keyword는 해당 페이지 내용과 관련 있는 img_keyword를 쓰는것이 좋습니다. 먼저 어떤 사진이 들어가야 사람들에게 후킹한 사진이 나올지 / 또 카드뉴스의 배경사진으로 쓰기 좋을지 생각한 뒤, 해당 사진을 얻기위한 일반적인 검색어가 무엇인지 생각해서 결정해야합니다. 내용과 꼭 100% 일치하지 않더라도, 관련있으면서 구글 이미지 검색시 배경으로 쓸만한 사진이 나올만한 검색어를 써야합니다. \n"
        "title쪽 img_keyword를 떠올릴때에는 (1)관련된 행위를 하는 연예인(여: 장원영|유나|카리나|설윤, 남:차은우|방탄소년단 뷔) 사진을 활용하는 전략, (2) 그냥 해당 페이지와 관련있는 최대한 재미있거나 쇼킹하거나 후킹한 사진, (3)1,2와 같은 사진이 없을것 같은 주제이면 그냥 내용과 관련있는 사진을 쓰는것이 좋습니다.\n"
        "만약 연예인 사진을 쓴다면, 컨텐츠의 주 독자가 남성이면 여자연예인을, 여성이면 그 반대 사진을 쓰는것이 좋습니다.\n"
        "꼭 필요한 경우가 아니면 한자는 쓰지마. 기본적으로는 한글로 쓰는게 좋아.\n"
        "다른 텍스트를 출력하지 말고 꼭 Json 형식의 출력만 하세요! 백틱json도 쓰지말고 그냥 대괄호,중괄호'[{' 로 바로 시작하도록.\n"
        "---참조할 검색 결과---\n"
        "{page_texts}")
)


NEWS_MAKER = Agent(
    name="news_maker",
    model=LiteLlm(model=MODEL_HIGH),
    instruction=(
        "아래 검색 결과를 바탕으로 '{keyword}'에 대한 뉴스에 대한 카드뉴스 list(dict) 형식의 JSON으로 2장(첫 타이틀 페이지와, 둘째 페이지: 뉴스내용에 대한 요약 페이지)을 출력하세요.\n"
        "- 첫 dict: title, img_keyword 를 key로 가지는 dict\n"
        "- 이후 dict: body, img_keyword를 key로 가지는 dict\n"
        "뉴스 기사에 대한 팩트(아래 검색 내용)를 기반으로, 사용자가 요청한 키워드에 대한 카드뉴스를 출력하세요. 꼭 아래 검색 내용에 있는 내용으로 카드뉴스를 출력해야 합니다.\n"
        "img_keyword는 해당 뉴스 내용에 어울리며 후킹한 이미지를 검색하기 위한 구글 검색어를 써야합니다. 먼저 어떤 사진이 들어가야 사람들에게 후킹한 사진이 나올지 생각한 뒤, 해당 사진을 얻기위한 일반적인 검색어가 무엇인지 생각해서 결정해야해. 내용과 꼭 100% 일치하지 않더라도, 관련있으면서 구글 이미지 검색시 배경으로 쓸만한 사진이 나올만한 검색어를 써야합니다.\n"
        "body는 2~4문장, 최대 150자 이내로 써야합니다. 꼭 최대 글자수를 채울 필요는 없지만, 독자들이 흥미로워할 내용이 많다면 길게, 아니라면 짧게 쓰고 넘어가는게 좋습니다."
        "꼭 필요한 경우가 아니면 한자는 쓰지마. 기본적으로는 한글로 쓰는게 좋아.\n"
        "다른 텍스트를 출력하지 말고 꼭 Json 형식의 출력만 하세요! 백틱json도 쓰지말고 그냥 대괄호,중괄호'[{' 로 바로 시작하도록.\n"
        "---참조할 검색 결과---"
        "{page_texts}")
)

# ---------------------------------------------------------------------------
# Runner 실행 후 최종 응답 헬퍼
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

async def generate_cardnews(client, keyword: str, date_range: str = None) -> str:

    if date_range == "None":
        date_range = None
    service = InMemorySessionService()
    service.create_session(app_name="app", user_id="user", session_id="sess")
    session = service.get_session(app_name="app", user_id="user", session_id="sess")


    service.append_event(
        session,
        Event(invocation_id="set_pages",
            author="system",
            actions=EventActions(state_delta={"keyword": keyword}))
    )

    # 1️⃣ 분류
    runner_cls = Runner(agent=CLASSIFY_AGENT, app_name="app", session_service=service)
    category = (await _run_agent(runner_cls, keyword)).strip()
    service.append_event(
        session,
        Event(invocation_id="set_pages",
            author="system",
            actions=EventActions(state_delta={"category": category}))
    )

    print("====== category ======")
    print(category)

    # 2️⃣ 검색 + 필터
    search_results = await search_google(client, keyword, date_range)
    print("====== search_results ======")
    print("search_results count:", len(search_results))
    print(search_results)

    service.append_event(
        session,
        Event(invocation_id="set_pages",
            author="system",
            actions=EventActions(state_delta={"search_results": search_results}))
    )

    runner_flt = Runner(agent=FILTER_AGENT, app_name="app", session_service=service)
    selected_json = await _run_agent(runner_flt, "filter")

    print("=====크롤링 대상 url=====")
    print(selected_json)
    selected_url_list= safe_parse_urls(selected_json)
    selected_url_list = clean_urls(selected_url_list)
    print(selected_url_list)

    # 3️⃣ 페이지 텍스트 수집
    """
    texts = ""
    for i, url in enumerate(selected_url_list):
        print("cawling start:", url)
        try:
            page_text= await fetch_page_text(client, url)
            print(url)
            print(page_text)
            texts+=f"---{i+1}번째 페이지---\n"
            texts+=page_text[:10000]
            texts+="--------------------------------\n"
        except Exception:
            continue
        print("cawling end", url)
    """
    page_texts = await parallel_fetch_texts(client, selected_url_list, max_concurrency=5)


    service.append_event(
        session,
        Event(invocation_id="set_pages",
            author="system",
            actions=EventActions(state_delta={"page_texts": page_texts}))
    )
    print("====== crawled text context=======")
    print(page_texts)



    # 4️⃣ 카드뉴스 생성
    if category == "장소":
        maker_agent = RESTAURANT_MAKER
        category_for_json = "place"
    elif category == "꿀팁":
        maker_agent = TIPS_MAKER
        category_for_json = "text"
    elif category == "뉴스":
        maker_agent = NEWS_MAKER
        category_for_json = "news"
    else: 
        raise ValueError("Invalid category")

    runner_mkr = Runner(agent=maker_agent, app_name="app", session_service=service)

    # 5 이미지 url_list 까지 카드뉴스에 병합
    raw_json = await _run_agent(runner_mkr, "generate")

    # -------- img_keyword → 이미지 검색 결과로 치환 --------
    try:
        pages = json.loads(raw_json)
    except:
        import pdb; pdb.set_trace()

    async def _enrich_page(page):
        if "img_keyword" not in page:
            return page
        kw = page["img_keyword"]
        img_res = await search_google_images(client, kw, top_k=20)
        page["img_urls"]  = [r["img_url"] for r in img_res]
        page["ref_urls"]  = [r["ref_urls"]     for r in img_res]
        page["img_desc"]  = [r["img_desc"]    for r in img_res]
        return page

    # 병렬 실행 (동시 5개 제한)
    sem   = asyncio.Semaphore(5)
    async def _wrapper(p):
        async with sem:
            return await _enrich_page(p)

    pages = await asyncio.gather(*[_wrapper(p) for p in pages])

    #최종적으로 카드뉴스 형식에 맞게 변환
    res_json={}
    res_json["category"] = category_for_json
    res_json["cards"] = pages
    res_json["desc"] = "default descriptions"


    return json.dumps(res_json, ensure_ascii=False, indent=None)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent.py <keyword>")
        sys.exit(1)

    kw = sys.argv[1]
    client = ProxyRotationClient()
    output = asyncio.run(generate_cardnews(client, kw, None)) # d, w, m, m3, y, None
    #output을 .txt파일로 저장
    with open("json_output.txt", "w") as f:
        f.write(output)

    # output을 json 형식으로 파싱
    output_json = json.loads(output)
    # print
    print(f"category: {output_json['category']}")
    print(f"desc: {output_json['desc']}")
    for i, card in enumerate(output_json['cards']):
        print(f"[{i+1}] card")
        if 'title' in card:
            print("title:", card['title'])
        if 'sub_title' in card:
            print("sub_title:", card['sub_title'])
        if 'body' in card:
            print("body:", card['body'])
        if 'img_keyword' in card:
            print("img_keyword:", card['img_keyword'])
        #if 'img_urls' in card:
        #    print(card['img_urls'])
        #if 'ref_urls' in card:
        #    print(card['ref_urls'])
        #if 'img_desc' in card:
        #    print(card['img_desc'])
        print("--------------------------------")
