def test_core_package_imports_without_optional_frameworks():
    import alephantai

    assert alephantai.__version__ == "0.1.0"
