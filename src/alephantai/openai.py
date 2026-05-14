from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Mapping, Optional

from .context import AlephantGatewayContext

if TYPE_CHECKING:
    from openai import OpenAI

DEFAULT_GATEWAY_BASE_URL = "https://ai.alephant.io/v1"


def merge_default_headers(
    user_headers: Optional[Mapping[str, str]],
    context_headers: Mapping[str, str],
) -> Dict[str, str]:
    """Merge headers with Alephant context headers winning case-insensitively."""
    merged = dict(user_headers or {})
    context_lower = {name.lower() for name in context_headers}
    for name in list(merged):
        if name.lower() in context_lower:
            del merged[name]
    merged.update(context_headers)
    return merged


def create_openai_client(
    api_key: str,
    context: Optional[AlephantGatewayContext] = None,
    base_url: str = DEFAULT_GATEWAY_BASE_URL,
    default_headers: Optional[Mapping[str, str]] = None,
    **kwargs: object,
) -> OpenAI:
    """Create an OpenAI-compatible client configured for Alephant Gateway."""
    from openai import OpenAI

    ctx = context or AlephantGatewayContext()
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers=merge_default_headers(default_headers, ctx.headers()),
        **kwargs,
    )
