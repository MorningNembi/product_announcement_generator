# 14-YG-AI

### 사용 방법
> 1. python3 -m venv .venv

> 2. source .venv/bin/activate

> 3. pip install --upgrade pip (생략 가능)

> 4. pip install -r requirements.txt

> 5. python main.py

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
