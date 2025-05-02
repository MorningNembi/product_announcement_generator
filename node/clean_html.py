from bs4 import BeautifulSoup
from langchain_core.documents import Document
from typing import Dict
from config import node_log


def html_clean(state: Dict) -> Dict:
    """
    • state['html'] 리스트의 첫 Document.page_content 에서
      태그·스크립트 제거 후 순수 텍스트로 변환
    • 다시 state['html'] = [Document(text,…)]
    """
    node_log("CLEANING HTML TAG")
    html = state["html"][0].page_content
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    # Document 리스트로 감싸서 다음 노드에 전달
    state["html"] = [Document(page_content=text, metadata={"source": state["url"]})]
    return state
