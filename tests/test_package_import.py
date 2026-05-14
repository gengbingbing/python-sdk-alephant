import importlib
import sys


def test_core_package_imports_without_optional_frameworks():
    import alephantai

    assert alephantai.__version__ == "0.1.0"


def test_core_package_import_does_not_import_openai_dependency():
    sys.modules.pop("alephantai", None)
    sys.modules.pop("alephantai.openai", None)
    sys.modules.pop("openai", None)

    importlib.import_module("alephantai")

    assert "openai" not in sys.modules
