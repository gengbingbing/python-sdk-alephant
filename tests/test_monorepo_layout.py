from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_alephantai_package_lives_under_packages_directory():
    package_root = ROOT / "packages" / "alephantai"

    assert (package_root / "pyproject.toml").is_file()
    assert (package_root / "src" / "alephantai" / "__init__.py").is_file()
    assert (package_root / "tests").is_dir()


def test_langchain_alephantai_has_independent_package_boundary():
    package_root = ROOT / "packages" / "langchain-alephantai"

    assert (package_root / "pyproject.toml").is_file()
    assert (package_root / "src" / "langchain_alephantai" / "__init__.py").is_file()
    assert (package_root / "tests").is_dir()
