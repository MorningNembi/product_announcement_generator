# 14-YG-AI

### 사용 방법
> 1. python3 -m venv .venv

> 2. source .venv/bin/activate

> 3. pip install --upgrade pip (생략 가능)

> 4. pip install -r requirements.txt

> 5. python app.py


### API 명세
## 상품 상세 설명 생성

- **Method:** `POST`
- **Endpoint:** `/generation/description`

### ✅ 요청 예시
```json
{
  "url": "https://myprotein/link"
}
```

### 📌 요청 파라미터

- **필수**
  - `url`: string  
- **선택**
  - (없음)

---

### ✅ 응답: 200 OK
```json
{
  "message": "상품 상세 설명이 생성되었습니다.",
  "data": {
    "product_name": "건강 햇반 3종 혼합 세트 (백미10 흑미10 발아현미10)",
    "product_lower_name": "햇반",
    "total_price": 58390,
    "count": 30,
    "summary": "햇반 컵반, 간편하고 맛있는 한 끼🍚를 찾는 당신에게 딱! 👍 오뚜기 컵밥보다 맛있다는 평가에 순한 카레맛, 
                낙지 콩나물 비빔밥 등 다양한 맛까지! 😋 햇반 솥반은 소고기우엉 영양밥으로 건강도 챙기세요! 💪 
                전자레인지 2분이면 완성되는 든든한 식사, 햇반과 함께하세요! ✨"
  }
}
```

---

### ⚠️ 응답: 400 Bad Request
```json
{
  "message": "유효하지 않은 URL 형식입니다.",
  "data": null
}
```

---

### 🔥 응답: 500 Internal Server Error
```json
{
  "message": "서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
  "data": null
}
```

### 0502
```mermaid
flowchart TD
subgraph Config[recursion_limit=15]
    end
subgraph Router_graph["Routing"]
    Start(URL) --> Router[/Router/]
    Router --> fetch_html_tool
    Router --> vision_model_parser
end
    direction TB
    hallucination_check1[hallucination_check: Groundedness Evaluator]
    hallucination_check2[hallucination_check: Groundedness Evaluator]
    fetch_html_tool --> clean_html
	vision_model_parser --> split_text
	clean_html --> split_text

subgraph RAG["RAG Pipeline"]
direction TB
    split_text([split_text])
    embed_texts([embed_texts])
    vector_search([vector_search])
    split_text --> embed_texts
    embed_texts --> vector_search
    vector_search --> LLM1(LLM: Product Announcement Parser)
end
    
    
    LLM1 --> hallucination_check1
    hallucination_check1 -->|불만족: rewirte_retrieve_query| vector_search
    hallucination_check1 -->|만족: JSON| web_search
    web_search --> LLM2(LLM: Product Description Generator)
    LLM2 --> hallucination_check2
    hallucination_check2 -->|만족| End(Product Information Summary)
    hallucination_check2 -->|불만족: rewrite_websearch_query| web_search
```
