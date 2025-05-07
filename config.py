import os
from dotenv import load_dotenv

load_dotenv()

# ── 민감정보 ───────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST")
VERTEX_API_KEY = os.getenv("VERTEX_API_KEY")

# ── 엔진 & 모델 설정 (4단계) ─────────────
# openai, vertexai, ollama
# gpt-4o, gemini-1.5-pro

## Router LLM 설정
# LLM_PROVIDER = "openai"
# MODEL_NAME = "gpt-4o"
LLM_PROVIDER = "vertexai"
# MODEL_NAME = "gemini-2.0-flash-001"
MODEL_NAME = "gemini-1.5-pro-002"

if LLM_PROVIDER == "vertexai":
    GCP_PROJECT = os.getenv("GCP_PROJECT")
    GCP_LOCATION = os.getenv("GCP_LOCATION")

LLM_PROVIDER_ROUTER = LLM_PROVIDER
MODEL_NAME_ROUTER = MODEL_NAME

## Summerize LLM 설정
LLM_PROVIDER_GENERATOR = LLM_PROVIDER
MODEL_NAME_GENERATOR = MODEL_NAME

# Hollucination Check LLM 설정
LLM_PROVIDER_GRADER = LLM_PROVIDER
MODEL_NAME_GRADER = MODEL_NAME

# Rewite query LLM 설정
LLM_PROVIDER_REWRITER = LLM_PROVIDER
MODEL_NAME_REWRITER = MODEL_NAME

# ── 일반 설정 ───────────────────────────
RECURSION_LIMIT = int(os.getenv("RECURSION_LIMIT", 15))
# VERBOSE_NODES = os.getenv("VERBOSE_NODES", "false").lower() in ("1", "true", "yes")
VERBOSE_NODES = False


def node_log(name: str):
    """
    노드가 실행될 때 한 줄만 찍어주는 헬퍼.
    .env 의 VERBOSE_NODES 에 따라 on/off 됨.
    """
    if VERBOSE_NODES:
        print(f"==== [{name}] ====")


# ── 프롬프트 템플릿 상수 ─────────────────
RAG_Query = (
    """"상품설명, 이름, 가격, 성분, 특이상항 등 가장 메인인 상품에 대한 구체적인 설명"""
)

# html로 가져올 도메인 목록
html_domain = ["myprotein"]
ROUTER_PROMPT = f"""You are an expert at routing a url to a fetch_html_tool and parse_image_text.
fetch_html_tool : url that is from {html_domain}
parse_image_text : any URL that is NOT from {html_domain}
"""

PRODUCT_ANNC_PARCER_PROMPT = """
다음은 HTML에서 텍스트만 추출한 상품 페이지 정보입니다.  
여러 종류의 부가 정보(브랜드, 리뷰, 배송 안내, 카테고리, 프로모션 등)가 혼합되어 있습니다.

아래 세 필드를 반드시 JSON 형식으로만 응답하세요:
- product_name (문자열): 실제 상품명. 입력 텍스트에서 가장 먼저 등장하는 정식 상품명을 그대로 사용합니다.
- product_lower_name (문자열): 상품의 대중적인 이름. 상품을 포함하는 카테고리를 의미합니다. 상품명에서 불필요한 정보는 제거합니다. 예: 즉석백미밥 직은공기 130g 36개입 -> 즉석백미밥
- total_price (정수): 최종 판매가(할인 적용 후). ‘원’ 단위를 제거하고 숫자만 추출합니다.
- count (정수): 판매 단위. 묶음의 개수. “2개”, “'500g x 2팩'에서 2팩” 등 표기된 수량을 파싱합니다. 개수 단위가 있는지 반드시 확인하고 파싱합니다, 수량 표기가 없으면 1로 간주합니다. 단위는 제거합니다.

# context: {context}

# 예시 출력 스키마: {format_instructions}
"""


# 수정 해야함 node_log("Generate Product Description")
PRODUCT_DESC_GEN_PROMPT = """
당신은 특정 제품을 검색한 결과로부터 제품에 대한 특징을 추출해 홍보글을 만들어주는 전문가 AI입니다. 
            사용자가 쉽게 이해할 수 있도록 중요한 제품 정보를 한국어로 자세하고 정확하게 요약하세요. 
            제품의 주요 특징, 장점 등을 포함하되, 주어진 내용에 없는 정보는 추측하지 마세요.
            중간중간 적절한 이모지를 사용하고, 판매하기 위한 홍보글 형식으로 만들어주세요.
            제품을 검색한 결과는 다음과 같습니다.   

# context: {context}

# 5문장 이내로 홍보글을 만들어주세요. 
"""

HALLU_PROMPT = """당신은 상품 정보 검증을 위한 단순 평가자입니다.
아래에 ‘원문’(Set of facts)과 ‘생성 결과’(LLM generation)가 주어집니다.
1) 각 필드(product_name, count, price)에 대해:
   - 원문에 정확히 존재하면 YES,  
   - 그렇지 않으면 NO  
2) 필드 검증이 모두 YES면 “overall”을 NO(→ 할루시네이션 아님),
   하나라도 NO면 “overall”을 YES(→ 할루시네이션)로 판단하세요.
반드시 아래 JSON 형식을 그대로 지켜 응답하세요."""

REWRITE_PROMPT_SYSTEM = """You a question re-writer that converts an input question to a better version that is optimized \n 
     for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""

REWRITE_PROMPT_HUMAN = """사용자가 입력한 검색어는 다음과 같습니다: {retriever_query}
            이 검색어를 검색기에서 가장 관련성 높은 결과를 찾을 수 있도록,
            • 주요 정보({generation})를 추가하고  
            • 불필요한 설명을 제거하며(무게, 개수 등)
            • 전체 문맥을 잘 반영하는 구체적인 질의 문장으로 다시 작성해 주세요."""
