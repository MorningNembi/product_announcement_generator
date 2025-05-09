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
        # 마프 오메가3
        # "url": "https://www.myprotein.co.kr/p/sports-nutrition/essential-omega-3/10529329/",
        # 11번가 방토
        # "url": "https://www.11st.co.kr/products/5351424764",
        # 쿠팡 햇반
        # "url": "https://www.coupang.com/vp/products/8426618994?vendorItemId=85588196697&sourceType=HOME_PERSONALIZED_ADS&searchId=feed-bee41ae7dc6246a3a2d87116f2d683a0-personalized_ads&clickEventId=117be320-20d5-11f0-9ac6-081d5860c7f0&isAddedCart=",
        # 네이버 몬스터
        # "url": "https://brand.naver.com/monsterenergy/products/10366088155?nl-query=몬스터&nl-au=d69982f4b9284de5b537e43cc055bdf9&NaPm=ci%3Dd69982f4b9284de5b537e43cc055bdf9%7Cct%3Dmaf2cm4c%7Ctr%3Dnslpsb%7Csn%3D%7Chk%3D4e7e6859930dc7d23e9c6af9ae5a3b262919baf6",
        # "url": "https://www.myprotein.co.kr/p/sports-nutrition/impact-whey-protein-powder/10530943/?variation=14302236",
        # "url": "https://www.11st.co.kr/products/pa/7812983055?trTypeCd=03&trCtgrNo=2171960"
        # "url": "https://www.gsshop.com/prd/prd.gs?prdid=13866536&lseq=390802-7&gsid=ECmain-AU390802-AU390802-7&dseq=7&svcid=pc&bnclick=main-mrcm_mainMrcmA_PopularCateItemUirm&rank=7"
        # "url": "https://www.gmarket.co.kr/item?goodsCode=2851959050&ver=20231001",
        "url": "https://brand.naver.com/basic-s/products/11065832613?NaPm=ct%3Dmagf3dxo%7Cci%3DER22e85952%2D2c9f%2D11f0%2Dafb4%2Deeae0d0a113e%7Ctr%3Dpla%7Chk%3Defd792d975085a0864d50e136bc8988dd9ac7691%7Cnacn%3D4UsnBcgvbXnU"
    }
    local_test(test_inputs)
