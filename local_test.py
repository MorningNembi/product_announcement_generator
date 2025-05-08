from config import RECURSION_LIMIT
from langchain_core.runnables import RunnableConfig
from langchain_teddynote.messages import random_uuid
from graph import app
from graph_output import invoke_graph, invoke_graph_clean, invoke_graph_json
import sys

# traceback을 아예 안 보여주도록 설정
sys.tracebacklimit = 0


def local_test(inputs: dict):
    """
    딕셔너리 형태의 inputs를 받아 LangGraph 워크플로우를 실행합니다.
    예시) main({"url": "https://...product_page..."})
    """
    # 1) RunnableConfig 생성
    config = RunnableConfig(
        recursion_limit=RECURSION_LIMIT, configurable={"thread_id": random_uuid()}
    )
    # 2) 그래프 실행
    # invoke_graph(app, inputs, config, node_names=["product_desc_gen"])
    # invoke_graph_clean(app, inputs, config, node_names=["product_desc_gen"])
    invoke_graph_json(app, inputs, config, node_names=["product_desc_gen"])


# 아래 코드는 스크립트로 직접 실행할 때, 기본 URL을 넣어주는 예시입니다.
if __name__ == "__main__":
    # 디폴트 테스트 URL 혹은 JSON 파싱 등을 여기에 넣어두셔도 되고
    test_inputs = {
        # "url": "https://www.myprotein.co.kr/p/sports-nutrition/essential-omega-3/10529329/",
        # "url": "https://www.11st.co.kr/products/5351424764",
        # "url": "https://www.coupang.com/vp/products/8426618994?vendorItemId=85588196697&sourceType=HOME_PERSONALIZED_ADS&searchId=feed-bee41ae7dc6246a3a2d87116f2d683a0-personalized_ads&clickEventId=117be320-20d5-11f0-9ac6-081d5860c7f0&isAddedCart=",
        # "url": "https://www.11st.co.kr/products/8154233165?&trTypeCd=MAS101&trCtgrNo=585021&checkCtlgPrd=true"
        "url": "https://brand.naver.com/monsterenergy/products/10366088155?nl-query=몬스터&nl-au=d69982f4b9284de5b537e43cc055bdf9&NaPm=ci%3Dd69982f4b9284de5b537e43cc055bdf9%7Cct%3Dmaf2cm4c%7Ctr%3Dnslpsb%7Csn%3D%7Chk%3D4e7e6859930dc7d23e9c6af9ae5a3b262919baf6"
        # "url": "https://www.coupang.com/vp/products/16494180?vendorItemId=92350969492&sourceType="
    }
    local_test(test_inputs)
