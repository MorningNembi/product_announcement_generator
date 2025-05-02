# llm/vertex_client.py
from typing import Any, Dict
from google.cloud import aiplatform
from llm.client import LLMClient
from config import GCP_PROJECT, GCP_LOCATION


class VertexClient(LLMClient):
    def __init__(self, model_name: str):
        # 1) 프로젝트와 리전 명시
        aiplatform.init(
            project=GCP_PROJECT,
            location=GCP_LOCATION,
        )
        # 2) ChatModel 로딩 (모델 이름은 "chat-bison@001" 같은 형식)
        self.chat_model = aiplatform.ChatModel.get_model(model_name)

    def chat(self, prompt: str, **kwargs) -> str:
        # prompt 키워드 인자가 바뀌었을 수 있으니, SDK 문서 확인
        response = self.chat_model.predict(prompt=prompt)
        return response.text

    def chat_structured(self, prompt_template, inputs: Dict[str, Any] = None):
        def _run(inp: Dict[str, Any]) -> str:
            text_prompt = prompt_template.format(**inp)
            return self.chat(text_prompt)

        if inputs is None:
            return _run
        return _run(inputs)
