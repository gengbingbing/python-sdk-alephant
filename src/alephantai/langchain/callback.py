from __future__ import annotations

import logging
from typing import Any, Optional

from alephantai.context import AlephantGatewayContext

logger = logging.getLogger(__name__)

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:

    class BaseCallbackHandler:  # type: ignore[no-redef]
        pass


class AlephantCallbackHandler(BaseCallbackHandler):
    """Lightweight LangChain callback that keeps an Alephant context available."""

    def __init__(
        self,
        *,
        context: Optional[AlephantGatewayContext] = None,
        strict: bool = False,
    ) -> None:
        super().__init__()
        self.context = context or AlephantGatewayContext()
        self.strict = strict
        self.raise_error = strict

    def on_chain_start(self, serialized: Any, inputs: Any, **kwargs: Any) -> None:
        return None

    def on_chain_end(self, outputs: Any, **kwargs: Any) -> None:
        return None

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        if self.strict:
            logger.debug("Alephant LangChain callback observed chain error: %s", error)
        return None

    def on_llm_start(self, serialized: Any, prompts: Any, **kwargs: Any) -> None:
        return None

    def on_chat_model_start(self, serialized: Any, messages: Any, **kwargs: Any) -> None:
        return None

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        return None

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        if self.strict:
            logger.debug("Alephant LangChain callback observed LLM error: %s", error)
        return None
