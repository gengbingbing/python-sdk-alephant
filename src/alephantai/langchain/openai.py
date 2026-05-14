from __future__ import annotations

from typing import Optional

from alephantai.context import AlephantGatewayContext
from alephantai.openai import DEFAULT_GATEWAY_BASE_URL, merge_default_headers


def create_chat_openai(
    api_key: str,
    model: str,
    context: Optional[AlephantGatewayContext] = None,
    base_url: str = DEFAULT_GATEWAY_BASE_URL,
    **kwargs: object,
):
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise ImportError(
            'Install LangChain support with: pip install "alephantai[langchain]"'
        ) from exc

    ctx = context or AlephantGatewayContext()
    default_headers = merge_default_headers(
        kwargs.pop("default_headers", None),
        ctx.headers(),
    )
    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        default_headers=default_headers,
        **kwargs,
    )
