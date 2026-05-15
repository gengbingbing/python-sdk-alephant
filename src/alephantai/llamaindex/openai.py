from __future__ import annotations

from typing import Optional

from alephantai.context import AlephantGatewayContext
from alephantai.openai import DEFAULT_GATEWAY_BASE_URL, gateway_default_headers


def create_openai_llm(
    *,
    api_key: str,
    model: str,
    context: Optional[AlephantGatewayContext] = None,
    base_url: str = DEFAULT_GATEWAY_BASE_URL,
    **kwargs: object,
):
    try:
        from llama_index.llms.openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            'Install LlamaIndex support with: pip install "alephantai[llamaindex]"'
        ) from exc

    ctx = context or AlephantGatewayContext()
    default_headers = gateway_default_headers(
        kwargs.pop("default_headers", None),
        ctx.headers(),
    )
    return OpenAI(
        api_key=api_key,
        api_base=base_url,
        model=model,
        default_headers=default_headers,
        **kwargs,
    )


def create_openai_embedding(
    *,
    api_key: str,
    model: str,
    context: Optional[AlephantGatewayContext] = None,
    base_url: str = DEFAULT_GATEWAY_BASE_URL,
    **kwargs: object,
):
    try:
        from llama_index.embeddings.openai import OpenAIEmbedding
    except ImportError as exc:
        raise ImportError(
            'Install LlamaIndex support with: pip install "alephantai[llamaindex]"'
        ) from exc

    ctx = context or AlephantGatewayContext()
    default_headers = gateway_default_headers(
        kwargs.pop("default_headers", None),
        ctx.headers(),
    )
    return OpenAIEmbedding(
        api_key=api_key,
        api_base=base_url,
        model=model,
        default_headers=default_headers,
        **kwargs,
    )
