import tomllib
from pathlib import Path

from un_schema_qa import __version__


def test_package_exposes_version() -> None:
    assert __version__ == "0.1.0"


def test_python_metadata_excludes_only_python_315() -> None:
    project_root = Path(__file__).parents[1]
    project_metadata = tomllib.loads(
        (project_root / "pyproject.toml").read_text(encoding="utf-8")
    )
    lock_metadata = tomllib.loads((project_root / "uv.lock").read_text(encoding="utf-8"))

    expected = ">=3.12,!=3.15.*"
    assert project_metadata["project"]["requires-python"] == expected
    assert lock_metadata["requires-python"].replace(" ", "") == expected
