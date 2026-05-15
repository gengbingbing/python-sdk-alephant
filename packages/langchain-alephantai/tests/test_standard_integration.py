import os
from typing import Type

import pytest
from langchain_tests.integration_tests import ChatModelIntegrationTests

from langchain_alephantai import ChatAlephantAI

pytestmark = pytest.mark.integration


class TestChatAlephantAIStandardIntegration(ChatModelIntegrationTests):
    @property
    def chat_model_class(self) -> Type[ChatAlephantAI]:
        return ChatAlephantAI

    @property
    def chat_model_params(self) -> dict:
        api_key = os.environ.get("ALEPHANT_API_KEY")
        if not api_key:
            pytest.skip("ALEPHANT_API_KEY is required for Alephant integration tests.")
        return {
            "api_key": api_key,
            "model": os.environ.get("ALEPHANT_TEST_MODEL", "gpt-4o-mini"),
            "session_name": "langchain-standard-integration",
        }
