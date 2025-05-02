# node/tool/fetch_html.py

from bs4 import BeautifulSoup
from langchain_core.documents import Document
import requests, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import Dict
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


def fetch_html_tool(state: Dict) -> Dict:
    """
    url을 받아 HTML을 가져와 state['html']에 Document 리스트로 저장한 뒤 state를 반환
    """
    node_log("FETCHING HTML")
    url = state["url"]
    html_str = None

    # 1) requests 시도
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        candidate = resp.text
        if not is_blocked(candidate):
            html_str = candidate
    except Exception as e:
        logger.info(f"requests 실패 ({e}), Selenium 폴백")

    # 2) requests가 안되거나 차단되면 Selenium 폴백
    if html_str is None:
        html_str = fetch_with_selenium(url)

    # 3) 최종 차단 확인
    if not html_str or is_blocked(html_str):
        raise RuntimeError(f"fetch_html 실패: {url}")

    # 4) 반드시 state에 Document 리스트로 저장
    state["html"] = [Document(page_content=html_str, metadata={"source": url})]
    return state
