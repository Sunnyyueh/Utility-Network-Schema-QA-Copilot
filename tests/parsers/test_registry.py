from pathlib import Path

import pandas as pd
import pytest

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import (
    InputParseError,
    ParsedDocument,
    ParsedSheet,
)
from un_schema_qa.parsers.registry import ParserRegistry, parse_document


def _write_minimal_fixture(path: Path) -> None:
    suffix = path.suffix.casefold()
    if suffix == ".csv":
        path.write_text("name\nMaterial\n", encoding="utf-8")
    elif suffix == ".xlsx":
        pd.DataFrame([{"name": "Material"}]).to_excel(path, index=False)
    elif suffix == ".json":
        path.write_text('[{"name": "Material"}]', encoding="utf-8")
    else:
        path.write_text("- name: Material\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("suffix", "expected_format"),
    [
        (".csv", InputFormat.CSV),
        (".xlsx", InputFormat.XLSX),
        (".json", InputFormat.JSON),
        (".yaml", InputFormat.YAML),
        (".yml", InputFormat.YAML),
        (".JsOn", InputFormat.JSON),
    ],
)
def test_parse_document_dispatches_by_suffix(
    tmp_path: Path,
    suffix: str,
    expected_format: InputFormat,
) -> None:
    path = tmp_path / f"schema{suffix}"
    _write_minimal_fixture(path)

    assert parse_document(path).input_format is expected_format


def test_fresh_registry_registers_and_invokes_structural_parser() -> None:
    path = Path("schema.CUSTOM")

    class StubParser:
        def __init__(self) -> None:
            self.seen_path: Path | None = None

        def parse(self, candidate: Path) -> ParsedDocument:
            self.seen_path = candidate
            return ParsedDocument(
                path=str(candidate),
                input_format=InputFormat.JSON,
                sheets=(ParsedSheet(name="data"),),
            )

    parser = StubParser()
    registry = ParserRegistry()
    registry.register(".custom", parser)

    document = registry.parse(path)

    assert document.path == str(path)
    assert parser.seen_path == path


def test_parse_document_is_reexported_from_parsers_package(tmp_path: Path) -> None:
    from un_schema_qa.parsers import parse_document as public_parse_document

    path = tmp_path / "schema.json"
    path.write_text('[{"name": "Material"}]', encoding="utf-8")

    assert public_parse_document(path).input_format is InputFormat.JSON


def test_parse_document_rejects_unknown_suffix(tmp_path: Path) -> None:
    path = tmp_path / "schema.txt"
    path.write_text("name", encoding="utf-8")

    with pytest.raises(InputParseError, match="FORMAT_UNSUPPORTED") as exc_info:
        parse_document(path)

    error = exc_info.value
    assert error.code == "FORMAT_UNSUPPORTED"
    assert error.path == path
    assert error.detail == "unsupported suffix '.txt'"
    assert error.__cause__ is None


def test_parse_document_rejects_missing_suffix(tmp_path: Path) -> None:
    path = tmp_path / "schema"
    path.write_text("name", encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        parse_document(path)

    error = exc_info.value
    assert error.code == "FORMAT_UNSUPPORTED"
    assert error.path == path
    assert error.detail == "unsupported suffix ''"
    assert error.__cause__ is None
