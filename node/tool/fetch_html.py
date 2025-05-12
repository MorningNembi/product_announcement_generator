# node/tool/fetch_html.py

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
