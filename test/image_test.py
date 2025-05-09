# tests/test_app.py
import pytest
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from fastapi.testclient import TestClient

client = TestClient(app)

# 1) 정상 동작 케이스: (URL, 예상 lower_name, 예상 total_price, 예상 count)
@pytest.mark.parametrize("url, exp_lower, exp_price, exp_count", [
    (
        "https://brand.naver.com/monsterenergy/products/10366088155?nl-query=%EB%AA%AC%EC%8A%A4%ED%84%B0&nl-au=d69982f4b9284de5b537e43cc055bdf9",
        "본스터 에너지", 19980, 12
    ),
    (
        "https://www.coupang.com/vp/products/8386250850?vendorItemId=90475442549&sourceType=HOME_PERSONALIZED_ADS&searchId=feed-8172ec1fe4b74be8bf39e99abb716ed2-personalized_ads&clickEventId=6ef7bf40-2a91-11f0-a1e3-e41ffcb2f197&isAddedCart=",
        "햇반", 58390, 30
    ),
    (
        "https://www.11st.co.kr/products/5351424764",
        "스윗마토 방울토마토", 10500, 2
    ),
])

def test_generation_success(url, exp_lower, exp_price, exp_count):
    # API 호출
    resp = client.post("/generation/description", json={"url": url}, timeout = 120)
    assert resp.status_code == 200

    body = resp.json()
    # 메시지 확인
    assert body["message"] == "상품 상세 설명이 생성되었습니다."
    # 데이터 필드 확인
    data = body["data"]
    assert data["product_lower_name"] == exp_lower
    assert data["total_price"] == exp_price
    assert data["count"] == exp_count

    assert isinstance(data["summary"], str) and len(data["summary"]) > 0

    # 루트에 screenshot.png 가 생성되었는지 확인
    assert os.path.exists("./img/screenshot.png"), "스크린샷 파일이 없습니다"
    assert os.path.getsize("./img/screenshot.png") > 0, "스크린샷 파일이 비어 있습니다"

    time.sleep(30)


# def test_generation_failure(monkeypatch):

#     import generate_product_announcement as gpa_module

#     def fake_raise(arg):
#         raise RuntimeError("forced error")
#     monkeypatch.setattr(gpa_module, "generate_product_announcement", fake_raise)

#     resp = client.post("/generation/description", json={"url": "https://example.com"})
#     assert resp.status_code == 200

#     body = resp.json()
#     # 오류 메시지 및 data=null 확인
#     assert body["message"] == "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
#     assert body["data"] is None
