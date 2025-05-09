# node/tool/fetch_html.py

from bs4 import BeautifulSoup
from langchain_core.documents import Document
import requests, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import Dict, Any
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
    opts.add_argument("--headless")
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(timeout)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html


def fetch_html_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    • state['url'] 에서 우선 requests로 가져옵니다.
    • 만약 차단 의심(is_blocked) 이거나,
      BeautifulSoup.get_text() 결과 길이가 짧으면
    • Selenium으로 완전 렌더링한 HTML을 대신 사용합니다.
    """
    node_log("FETCHING HTML")
    url = state.get("url")
    if not url:
        raise ValueError("fetch_html_tool: state에 'url'이 없습니다.")

    html_str: str = ""
    # 1) requests 시도
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        candidate = resp.text

        # 2) 텍스트 길이 체크
        text_len = len(BeautifulSoup(candidate, "html.parser").get_text().strip())
        if is_blocked(candidate) or text_len < 300:
            node_log("STATIC fetch insufficient or blocked, using Selenium fallback")
            html_str = fetch_with_selenium(url)
        else:
            html_str = candidate

    except Exception as e:
        logger.info(f"requests fetch failed ({e}), switching to Selenium")
        html_str = fetch_with_selenium(url)

    # 3) 최종 차단 재확인
    if not html_str or is_blocked(html_str):
        raise RuntimeError(f"fetch_html 실패 (blocked or empty): {url}")

    # 4) Document 리스트로 감싸서 반환
    state["page"] = [Document(page_content=html_str, metadata={"source": url})]
    return state
