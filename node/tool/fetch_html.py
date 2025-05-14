# node/tool/fetch_html.py

import re
import json
from bs4 import BeautifulSoup
from langchain_core.documents import Document
import requests, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service 
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
from typing import Dict, Any
from config import node_log

logger = logging.getLogger(__name__)

def clean_html(state: Dict[str, Any]) -> Dict[str, Any]:
    # 1) 원본 HTML 가져오기
    raw_html = (
        state["page_html"][0].page_content
        if isinstance(state["page_html"], list) and hasattr(state["page_html"][0], "page_content")
        else state["page_html"]
    )

    # 2) BeautifulSoup으로 태그 제거 & 순수 텍스트 저장
    soup = BeautifulSoup(raw_html, "html.parser")
    state["page_html"] = soup.get_text(separator="\n", strip=True)

    pieces: list[str] = []

    # 3) <title>, meta.description, og:description, og:title
    if soup.title and soup.title.string:
        pieces.append(soup.title.string.strip())
    for sel in ("meta[name='description']", "meta[property='og:description']"):
        tag = soup.select_one(sel)
        if tag and tag.has_attr("content"):
            pieces.append(tag["content"].strip())
    tag = soup.select_one("meta[property='og:title']")
    if tag and tag.has_attr("content"):
        pieces.append(tag["content"].strip())

    # 4) script#data 내부 JSON 페이로드 (견본)
    data_tag = soup.select_one("script#data")
    if data_tag and data_tag.string:
        try:
            obj = json.loads(data_tag.string)
            for key in ("prdNo", "price", "content_category"):
                if key in obj:
                    pieces.append(f"{key}: {obj[key]}")
        except json.JSONDecodeError:
            pass

        # 5) 주요 JSON 키 패턴으로 가격 검색
    pattern_kv = r'"((?=[^"]*price)(?![^"]*last)[^"]*)"\s*:\s*([0-9]+(?:\.[0-9]+)?)'
    matches_kv = re.findall(pattern_kv, state["page_html"], flags=re.IGNORECASE)
    for key, val in matches_kv:
        if int(val) != 0:
            pieces.append(f"{key}: {val}")

    # 6) discounted price span 추출 (예: <span class="text-2xl font-semibold"> ₩12,600‎ </span>)
    price_tag = soup.select_one("span.text-2xl.font-semibold")
    if price_tag:
        # get_text() 로 “₩12,600‎” 같은 문자열을 꺼내고
        raw_price = price_tag.get_text(strip=True)
        # 숫자만 남기기
        digits = re.sub(r"[^\d]", "", raw_price)
        if digits:
            pieces.append(f"discounted_price: {digits}")
    print(pieces)
    state["page"] = "\n".join(pieces)

def is_blocked(content: str) -> bool:
    if not content or len(content) < 200:
        return True
    text = BeautifulSoup(content, "html.parser").get_text().lower()
    for kw in ["captcha", "robot", "blocked", "access denied", "too many requests"]:
        if kw in text:
            return True
    return False


def fetch_with_selenium(url: str, timeout: int = 15) -> str:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # opts.add_experimental_option(
    #     "mobileEmulation",
    #     {
    #         "deviceMetrics": {"width": 600, "height": height, "pixelRatio": 2.0},
    #         "userAgent": (
    #             "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
    #             "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 "
    #             "Mobile/15E148 Safari/604.1"
    #         ),
    #     },
    # )
    opts.add_argument("--ignore-certificate-errors")
    opts.set_capability("acceptInsecureCerts", True)

    # 드라이버 실행
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(
        service=service,
        options=opts
    )

    stealth(
        driver,
        languages=["ko-KR", "ko"],
        vendor="Google Inc.",
        platform="iPhone",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": "window.alert = ()=>{}; window.confirm = ()=>true; window.prompt = ()=>null;"
        },
    )

    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html


def fetch_html_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    node_log("FETCHING AND CLEANING HTML")
    url = state.get("url")
    if not url:
        raise ValueError("fetch_html_tool: state에 'url'이 없습니다.")

    state["page_html"] = ""
    try:
        # requests 타임아웃을 조금 늘릴 수도 있습니다.
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        candidate = resp.text

        text_len = len(BeautifulSoup(candidate, "html.parser").get_text().strip())
        if is_blocked(candidate) or text_len < 300:
            node_log("STATIC fetch insufficient or blocked, using Selenium fallback")
            state["page_html"] = fetch_with_selenium(url)
        else:
            state["page_html"] = candidate

    except requests.exceptions.ReadTimeout as e:
        logger.info(f"requests timeout ({e}), switching to Selenium")
        state["page_html"] = fetch_with_selenium(url)
    except Exception as e:
        logger.info(f"requests fetch failed ({e}), switching to Selenium")
        state["page_html"] = fetch_with_selenium(url)

    if not state["page_html"] or is_blocked(state["page_html"]):
        raise RuntimeError(f"fetch_html 실패 (blocked or empty): {url}")

    state["page_html"] = [Document(page_content=state["page_html"], metadata={"source": url})]

    clean_html(state)

    return state