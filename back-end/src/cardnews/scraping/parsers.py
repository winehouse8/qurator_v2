# get_parsed_google_img_search_page.py
from bs4 import BeautifulSoup, NavigableString, Tag
from typing import List, Dict, Optional



def _safe_text(node: Tag) -> str:
    """Return all text of a BeautifulSoup node (stripped) or empty string."""
    return node.get_text(" ", strip=True) if node else ""


def get_parsed_google_img_search_page(html: str) -> List[Dict[str, Optional[str]]]:
    """
    Parse a Google **이미지** 검색 결과 page and pull out
    description, landing-page URL, and thumbnail/preview image URL
    for every result card (`<div jsname="dTDiAc"> … </div>`).

    The DOM layout (2025-05) is roughly::

        <div jsname="dTDiAc">
            <div>                        <-- #1  (ignored)
            <div>                        <-- #2  [thumbnail]
                <img src="...">
            <div>                        <-- #3
                <a href="https://target.site/…">   <-- landing page
                    <div> …ignored… </div>
                    <div> description … </div>     <-- 2nd child div
                </a>
            ...
        </div>

    If a card lacks any of the three items it is silently skipped.
    YouTube / TikTok links are also skipped.

    Returns
    -------
    list[dict]
        Every dict has keys: ``desc``, ``url``, ``img_url``.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: List[Dict[str, str]] = []

    for card in soup.select('div[jsname="dTDiAc"]'):
        # --- img_url --------------------------------------------------------
        second_div = card.select_one(":scope > div:nth-of-type(2)")
        img_tag = second_div.find("img") if second_div else None
        img_url = img_tag.get("src") if img_tag else None

        # --- url & desc ------------------------------------------------------
        third_div = card.select_one(":scope > div:nth-of-type(3)")
        a_tag = third_div.find("a", href=True) if third_div else None
        url = a_tag["href"] if a_tag else None

        # description is the **second** child <div> beneath <a>
        desc_div = a_tag.select_one(":scope > div:nth-of-type(2)") if a_tag else None
        desc = _safe_text(desc_div)

        # --- filtering / validation -----------------------------------------
        if not (url and img_url and desc):
            continue  # incomplete card

        lowered = url.lower()
        if any(bad in lowered for bad in ("youtube.", "youtu.be", "tiktok.")):
            continue

        results.append(
            {
                "img_desc": desc,
                "ref_urls": url,
                "img_url": img_url,
            }
        )

    return results


def get_parsed_google_search_page(html: str) -> List[Dict[str, Optional[str]]]:
    """
    Parses a raw Google search result page (HTML) and extracts a list of
    dictionaries with 'desc' and 'url' keys, omitting any results whose URL
    contains 'youtube'.

    Args:
        html: The raw HTML string of the Google search results page.

    Returns:
        A list of dicts, each with:
          - 'desc': the text content of the result element
          - 'url' : the href of the first <a> tag inside that element, or None
    """
    soup = BeautifulSoup(html, "html.parser")
    parsed_results: List[Dict[str, Optional[str]]] = []

    # Google result containers often use the class "MjjYud"
    for el in soup.select(".MjjYud"):
        desc = el.get_text(strip=True)
        a_tag = el.find("a", href=True)
        url = a_tag["href"] if a_tag else None

        # Exclude any URL containing "youtube"
        if not url or len(url) < 5:
            continue

        if "youtube" in url.lower():
            continue
        if "tiktok" in url.lower():
            continue
        
        
        if len(str(url))<5:
            continue

        parsed_results.append({
            "desc": desc,
            "url": url
        })

    return parsed_results


def get_parsed_text_page(html: str) -> str:
    """
    Parses a raw HTML page and returns only the main content text,
    stripping out navigation, headers, footers, scripts, styles, and other
    non-content elements.

    Args:
        html: The raw HTML string of the page.

    Returns:
        A single string containing the page's visible content text.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Focus on the <body> if available
    root = soup.body or soup

    # Remove unwanted elements
    for selector in [
        "nav", "header", "footer", "aside",   # layout/navigation
        "script", "style", "noscript",        # code and styling
        "form", "img", "svg", "canvas",       # non-text media
        "[role=navigation]",                   # ARIA navigation
    ]:
        for el in root.select(selector):
            el.decompose()

    # Extract and clean text
    text = root.get_text(separator=" ", strip=True)

    # Collapse multiple whitespace into single spaces
    return " ".join(text.split())
