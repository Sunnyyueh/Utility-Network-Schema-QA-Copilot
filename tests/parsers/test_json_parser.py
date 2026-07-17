from pathlib import Path

import pytest

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import InputParseError
from un_schema_qa.parsers.json_parser import JsonParser


def test_json_parser_reads_named_sheets(tmp_path: Path) -> None:
    path = tmp_path / "schema.json"
    path.write_text('{"fields": [{"name": "Material"}]}', encoding="utf-8")

    document = JsonParser().parse(path)

    assert document.input_format is InputFormat.JSON
    assert document.sheets[0].name == "fields"


def test_json_parser_wraps_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "schema.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(InputParseError, match="JSON_PARSE_FAILED"):
        JsonParser().parse(path)


def test_json_parser_maps_a_list_to_data_rows_and_preserves_path(tmp_path: Path) -> None:
    path = tmp_path / "schema.json"
    path.write_text('[{"name": "Material"}]', encoding="utf-8")

    document = JsonParser().parse(path)

    assert document.path == str(path)
    assert document.sheets[0].name == "data"
    assert document.sheets[0].rows == ({"name": "Material"},)


@pytest.mark.parametrize(
    ("contents", "cause_type"),
    [(None, FileNotFoundError), (b"\xff\xfe", UnicodeDecodeError)],
    ids=["missing", "invalid-utf8"],
)
def test_json_parser_wraps_file_errors(
    tmp_path: Path,
    contents: bytes | None,
    cause_type: type[BaseException],
) -> None:
    path = tmp_path / "schema.json"
    if contents is not None:
        path.write_bytes(contents)

    with pytest.raises(InputParseError) as exc_info:
        JsonParser().parse(path)

    error = exc_info.value
    assert error.code == "JSON_PARSE_FAILED"
    assert error.path == path
    assert error.detail
    assert isinstance(error.__cause__, cause_type)
    assert error.detail == str(error.__cause__)


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_json_parser_rejects_non_standard_numeric_constants(
    tmp_path: Path,
    constant: str,
) -> None:
    path = tmp_path / "schema.json"
    path.write_text(f'[{{"value": {constant}}}]', encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        JsonParser().parse(path)

    error = exc_info.value
    assert error.code == "JSON_PARSE_FAILED"
    assert error.path == path
    assert constant in error.detail
    assert error.__cause__ is not None


def test_json_parser_propagates_top_level_structure_errors(tmp_path: Path) -> None:
    path = tmp_path / "schema.json"
    path.write_text('"not-a-table"', encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        JsonParser().parse(path)

    error = exc_info.value
    assert error.code == "STRUCTURE_INVALID"
    assert error.path == path
    assert error.__cause__ is None


def test_json_parser_normalizes_named_sheets_deterministically(tmp_path: Path) -> None:
    path = tmp_path / "schema.json"
    path.write_text(
        '{"fields": [{"name": "Material"}], "domains": [{"code": 1}]}',
        encoding="utf-8",
    )

    document = JsonParser().parse(path)

    assert [sheet.name for sheet in document.sheets] == ["domains", "fields"]
    assert document.sheets[0].rows == ({"code": 1},)
    assert document.sheets[1].rows == ({"name": "Material"},)


def test_json_parser_does_not_modify_input_bytes(tmp_path: Path) -> None:
    path = tmp_path / "schema.json"
    original = b'{\r\n  "fields": [{"name": "Material"}]\r\n}\r\n'
    path.write_bytes(original)

    JsonParser().parse(path)

    assert path.read_bytes() == original
