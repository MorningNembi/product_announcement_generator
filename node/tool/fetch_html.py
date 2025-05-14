# node/tool/fetch_html.py

import re
import json
import logging
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

from config import node_log

logger = logging.getLogger(__name__)


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
    opts.add_argument("--ignore-certificate-errors")
    opts.set_capability("acceptInsecureCerts", True)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)

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
        {"source": "window.alert = ()=>{}; window.confirm = ()=>true; window.prompt = ()=>null;"},
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

    html_str = ""
    # 1) Try static fetch
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        candidate = resp.text

        text_len = len(BeautifulSoup(candidate, "html.parser").get_text().strip())
        if is_blocked(candidate) or text_len < 300:
            node_log("STATIC fetch insufficient or blocked, using Selenium fallback")
            html_str = fetch_with_selenium(url)
        else:
            html_str = candidate

    except Exception as e:
        logger.info(f"requests fetch failed ({e}), switching to Selenium")
        try:
            html_str = fetch_with_selenium(url)
        except Exception as ex:
            logger.error(f"Selenium fetch also failed ({ex}), returning empty page")
            state["page"] = ""
            return state

    # 2) If still blocked or empty, return empty
    if not html_str or is_blocked(html_str):
        state["page"] = ""
        return state

    # 3) Parse out <title>, meta, JSON and price patterns
    soup = BeautifulSoup(html_str, "html.parser")
    state["page_html"] = soup.get_text(separator="\n", strip=True)
    pieces: list[str] = []

    # <title>, meta.description, og:description, og:title
    if soup.title and soup.title.string:
        pieces.append(soup.title.string.strip())
    for sel in ("meta[name='description']", "meta[property='og:description']"):
        tag = soup.select_one(sel)
        if tag and tag.has_attr("content"):
            pieces.append(tag["content"].strip())
    tag = soup.select_one("meta[property='og:title']")
    if tag and tag.has_attr("content"):
        pieces.append(tag["content"].strip())

    # script#data 내부 JSON 페이로드
    data_tag = soup.select_one("script#data")
    if data_tag and data_tag.string:
        try:
            obj = json.loads(data_tag.string)
            for key in ("prdNo", "price", "content_category"):
                if key in obj:
                    pieces.append(f"{key}: {obj[key]}")
        except json.JSONDecodeError:
            pass

    # JSON 키 패턴으로 가격 검색
    pattern_kv = r'"((?=[^"]*price)(?![^"]*last)[^"]*)"\s*:\s*([0-9]+(?:\.[0-9]+)?)'
    for key, val in re.findall(pattern_kv, html_str, flags=re.IGNORECASE):
        if int(val) != 0:
            pieces.append(f"{key}: {val}")
    # 4) Set cleaned text or empty
    state["page"] = "\n".join(pieces) if pieces else ""
    return state
