from bs4 import BeautifulSoup
from langchain_core.documents import Document
from typing import Dict
from config import node_log


def vision_parser_tool(state: Dict) -> Dict:
    """
    url을 전달받아 해당 페이지의 상품정보를 비전 모델을 통해 파싱하여 텍스트를 가져오는 도구
    """
    node_log("COOPANG HTML")
    text = "None"
    state["html"] = [Document(page_content=text, metadata={"source": state["url"]})]
    return state
