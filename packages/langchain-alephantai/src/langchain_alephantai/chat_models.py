from __future__ import annotations

from typing import Optional

from alephantai import AlephantGatewayContext
from alephantai.openai import DEFAULT_GATEWAY_BASE_URL, gateway_default_headers
from langchain_openai import ChatOpenAI


class ChatAlephantAI(ChatOpenAI):
    """Chat model configured for Alephant AI Gateway."""

    @classmethod
    def get_lc_namespace(cls) -> list[str]:
        return ["langchain_alephantai", "chat_models"]

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return False

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        context: Optional[AlephantGatewayContext] = None,
        session_id: Optional[str] = None,
        session_name: Optional[str] = None,
        base_url: str = DEFAULT_GATEWAY_BASE_URL,
        **kwargs: object,
    ) -> None:
        ctx = context or AlephantGatewayContext(
            session_id=session_id,
            session_name=session_name,
        )
        default_headers = gateway_default_headers(
            kwargs.pop("default_headers", None),
            ctx.headers(),
        )
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model=model,
            default_headers=default_headers,
            **kwargs,
        )
