from config import (
    LLM_PROVIDER_ROUTER,
    MODEL_NAME_ROUTER,
    LLM_PROVIDER_GENERATOR,
    MODEL_NAME_GENERATOR,
    LLM_PROVIDER_GRADER,
    MODEL_NAME_GRADER,
    LLM_PROVIDER_REWRITER,
    MODEL_NAME_REWRITER,
)
from llm.client import LLMClient
from llm.openai_client import OpenAIClient
from llm.ollama_client import OllamaClient
from llm.vertex_client import VertexClient


def _get_client(provider: str, model_name: str, temperature=0) -> LLMClient:
    if provider == "openai":
        return OpenAIClient(model_name=model_name, temperature=temperature)
    if provider == "ollama":
        return OllamaClient(model_name=model_name)
    if provider == "vertex":
        return VertexClient(model_name=model_name, temperature=temperature)
    raise ValueError(f"Unknown LLM provider: {provider}")


def get_router_client() -> LLMClient:
    return _get_client(LLM_PROVIDER_ROUTER, MODEL_NAME_ROUTER)


def get_annc_parser_client() -> LLMClient:
    return _get_client(LLM_PROVIDER_GENERATOR, MODEL_NAME_GENERATOR)


def get_desc_gen_client() -> LLMClient:
    return _get_client(LLM_PROVIDER_GENERATOR, MODEL_NAME_GENERATOR, temperature=0.3)


def get_grader_client() -> LLMClient:
    return _get_client(LLM_PROVIDER_GRADER, MODEL_NAME_GRADER)


def get_rewriter_client() -> LLMClient:
    return _get_client(LLM_PROVIDER_REWRITER, MODEL_NAME_REWRITER)
