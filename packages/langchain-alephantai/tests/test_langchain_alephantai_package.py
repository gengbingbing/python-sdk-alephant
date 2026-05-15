import importlib


def test_langchain_alephantai_exports_existing_helper_api():
    package = importlib.import_module("langchain_alephantai")

    assert package.__version__ == "0.1.0"
    assert package.create_chat_openai.__name__ == "create_chat_openai"
    assert package.AlephantGatewayContext.__name__ == "AlephantGatewayContext"
