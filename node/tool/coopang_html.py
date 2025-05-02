from langchain_core.documents import Document
import logging
from typing import Dict
from config import node_log

logger = logging.getLogger(__name__)


def coopang_html_tool(state: Dict) -> Dict:
    """
    url을 전달받아 해당 페이지의 html을 가져오는 도구
    """
    node_log("COOPANG HTML")
    html = "None"

    state["html"] = [Document(page_content=html, metadata={"source": state["url"]})]
    return state
