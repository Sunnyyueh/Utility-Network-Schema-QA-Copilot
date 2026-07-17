from pathlib import Path

import pytest
import yaml

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import InputParseError
from un_schema_qa.parsers.yaml_parser import YamlParser


def test_yaml_parser_reads_named_sheets(tmp_path: Path) -> None:
    path = tmp_path / "schema.yaml"
    path.write_text("fields:\n  - name: Material\n", encoding="utf-8")

    document = YamlParser().parse(path)

    assert document.input_format is InputFormat.YAML
    assert document.sheets[0].rows[0]["name"] == "Material"


def test_yaml_parser_wraps_invalid_yaml(tmp_path: Path) -> None:
    path = tmp_path / "schema.yaml"
    path.write_text("fields: [", encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        YamlParser().parse(path)

    error = exc_info.value
    assert error.code == "YAML_PARSE_FAILED"
    assert error.path == path
    assert error.detail
    assert isinstance(error.__cause__, yaml.YAMLError)
    assert error.detail == str(error.__cause__)


def test_yaml_parser_maps_a_list_to_data_rows_and_preserves_path(tmp_path: Path) -> None:
    path = tmp_path / "schema.yaml"
    path.write_text("- name: Material\n", encoding="utf-8")

    document = YamlParser().parse(path)

    assert document.path == str(path)
    assert document.sheets[0].name == "data"
    assert document.sheets[0].rows == ({"name": "Material"},)


def test_yaml_parser_normalizes_named_sheets_deterministically(tmp_path: Path) -> None:
    path = tmp_path / "schema.yaml"
    path.write_text(
        "fields:\n  - name: Material\ndomains:\n  - code: 1\n",
        encoding="utf-8",
    )

    document = YamlParser().parse(path)

    assert [sheet.name for sheet in document.sheets] == ["domains", "fields"]
    assert document.sheets[0].rows == ({"code": 1},)
    assert document.sheets[1].rows == ({"name": "Material"},)


@pytest.mark.parametrize(
    ("contents", "cause_type"),
    [(None, FileNotFoundError), (b"\xff\xfe", UnicodeDecodeError)],
    ids=["missing", "invalid-utf8"],
)
def test_yaml_parser_wraps_file_errors(
    tmp_path: Path,
    contents: bytes | None,
    cause_type: type[BaseException],
) -> None:
    path = tmp_path / "schema.yaml"
    if contents is not None:
        path.write_bytes(contents)

    with pytest.raises(InputParseError) as exc_info:
        YamlParser().parse(path)

    error = exc_info.value
    assert error.code == "YAML_PARSE_FAILED"
    assert error.path == path
    assert error.detail
    assert isinstance(error.__cause__, cause_type)
    assert error.detail == str(error.__cause__)


def test_yaml_parser_rejects_unsafe_python_tag_without_execution(tmp_path: Path) -> None:
    side_effect = tmp_path / "unsafe-side-effect"
    path = tmp_path / "schema.yaml"
    path.write_text(
        f'!!python/object/apply:os.system ["touch {side_effect}"]\n',
        encoding="utf-8",
    )

    with pytest.raises(InputParseError) as exc_info:
        YamlParser().parse(path)

    error = exc_info.value
    assert error.code == "YAML_PARSE_FAILED"
    assert error.path == path
    assert error.detail
    assert isinstance(error.__cause__, yaml.YAMLError)
    assert not side_effect.exists()


@pytest.mark.parametrize("contents", ["not-a-table\n", ""], ids=["scalar", "empty"])
def test_yaml_parser_propagates_top_level_structure_errors(
    tmp_path: Path,
    contents: str,
) -> None:
    path = tmp_path / "schema.yaml"
    path.write_text(contents, encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        YamlParser().parse(path)

    error = exc_info.value
    assert error.code == "STRUCTURE_INVALID"
    assert error.path == path
    assert error.__cause__ is None


@pytest.mark.parametrize(
    "contents",
    ["- observed_at: 2026-07-17\n", "- value: .nan\n"],
    ids=["timestamp", "non-finite-number"],
)
def test_yaml_parser_propagates_non_json_row_errors(
    tmp_path: Path,
    contents: str,
) -> None:
    path = tmp_path / "schema.yaml"
    path.write_text(contents, encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        YamlParser().parse(path)

    error = exc_info.value
    assert error.code == "ROWS_INVALID"
    assert error.path == path


def test_yaml_parser_does_not_modify_input_bytes(tmp_path: Path) -> None:
    path = tmp_path / "schema.yaml"
    original = b"fields:\r\n  - name: Material\r\n"
    path.write_bytes(original)

    YamlParser().parse(path)

    assert path.read_bytes() == original


@pytest.mark.parametrize(
    "contents",
    [
        "fields: []\nfields: []\n",
        "- attributes:\n    name: first\n    name: second\n",
    ],
    ids=["top-level", "nested"],
)
def test_yaml_parser_rejects_duplicate_mapping_keys(
    tmp_path: Path,
    contents: str,
) -> None:
    path = tmp_path / "schema.yaml"
    path.write_text(contents, encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        YamlParser().parse(path)

    error = exc_info.value
    assert error.code == "YAML_PARSE_FAILED"
    assert error.path == path
    assert "duplicate key" in error.detail
    assert isinstance(error.__cause__, yaml.YAMLError)


def test_yaml_parser_wraps_recursive_alias_as_structured_input_error(
    tmp_path: Path,
) -> None:
    path = tmp_path / "schema.yaml"
    path.write_text("- &row\n  self: *row\n", encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        YamlParser().parse(path)

    error = exc_info.value
    assert error.code == "ROWS_INVALID"
    assert error.path == path
    assert "cyclic JSON value" in str(error.__cause__)
    assert not isinstance(error.__cause__, RecursionError)
