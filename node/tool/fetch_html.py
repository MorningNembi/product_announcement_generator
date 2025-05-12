# node/tool/fetch_html.py

from bs4 import BeautifulSoup
from langchain_core.documents import Document
import requests, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service  # 추가
from webdriver_manager.chrome import ChromeDriverManager  # 추가
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
    # Service 객체로 드라이버 경로 전달
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_page_load_timeout(timeout)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html


def fetch_html_tool(state: Dict[str, Any]) -> Dict[str, Any]:
    node_log("FETCHING HTML")
    url = state.get("url")
    if not url:
        raise ValueError("fetch_html_tool: state에 'url'이 없습니다.")

    html_str = ""
    try:
        # requests 타임아웃을 조금 늘릴 수도 있습니다.
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

    except requests.exceptions.ReadTimeout as e:
        logger.info(f"requests timeout ({e}), switching to Selenium")
        html_str = fetch_with_selenium(url)
    except Exception as e:
        logger.info(f"requests fetch failed ({e}), switching to Selenium")
        html_str = fetch_with_selenium(url)

    if not html_str or is_blocked(html_str):
        raise RuntimeError(f"fetch_html 실패 (blocked or empty): {url}")

    state["page"] = [Document(page_content=html_str, metadata={"source": url})]
    return state
