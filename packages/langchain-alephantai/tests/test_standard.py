from typing import Type

from langchain_tests.unit_tests import ChatModelUnitTests

from langchain_alephantai import ChatAlephantAI


class TestChatAlephantAIStandardUnit(ChatModelUnitTests):
    @property
    def chat_model_class(self) -> Type[ChatAlephantAI]:
        return ChatAlephantAI

    @property
    def chat_model_params(self) -> dict:
        return {
            "api_key": "vk-test",
            "model": "gpt-4o-mini",
            "session_id": "sess-standard-unit",
        }
