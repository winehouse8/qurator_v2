import ast, re, json
from typing import List, Dict

def safe_parse_urls(raw: str) -> List[str]:
    """LLM 이 돌려준 문자열을 최대한 유연하게 리스트로 변환."""
    raw = raw.strip()

    # ①  ```json ... ```  블록 제거
    if raw.startswith("```"):
        raw = re.sub(r"```[a-zA-Z]*\n?", "", raw)    # 앞/뒤 ``` 제거
        raw = raw.rstrip("`").rstrip()

    # ②  JSON 시도 (정상일 때 가장 빠름)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # ③  Python literal 시도 (작은따옴표 리스트 대응)
    try:
        return ast.literal_eval(raw)
    except Exception:
        raise ValueError("LLM returned unparsable URL list:\n" + raw)


def clean_urls(urls: List[str]) -> List[str]:
    """
    - 제거:   YouTube / TikTok URL
    - 변환:   https://blog.naver.com/*  →  https://m.blog.naver.com/*

    Args:
        urls: 원본 URL 리스트

    Returns:
        가공된 URL 리스트
    """
    cleaned: List[str] = []
    yt_tt = ("youtube.", "youtu.be", "tiktok.", "post.naver.")
    # blog.naver.com → m.blog.naver.com  (스킴 유지)
    blog_sub = re.compile(r"^https?://blog\.naver\.com/")

    for url in urls:
        if any(domain in url for domain in yt_tt):
            continue  # 필터링

        url = blog_sub.sub(lambda m: m.group(0).replace("://blog.", "://m.blog."), url)
        cleaned.append(url)

    return cleaned

