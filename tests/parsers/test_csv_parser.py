from pathlib import Path

import pandas as pd
import pytest

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import InputParseError
from un_schema_qa.parsers.csv_parser import CsvParser


def test_csv_parser_returns_records(tmp_path: Path) -> None:
    path = tmp_path / "schema.csv"
    path.write_text("name,data_type\nMaterial,string\n", encoding="utf-8")

    document = CsvParser().parse(path)

    assert document.path == str(path)
    assert document.input_format is InputFormat.CSV
    assert len(document.sheets) == 1
    assert document.sheets[0].name == "data"
    assert document.sheets[0].rows == ({"name": "Material", "data_type": "string"},)


def test_csv_parser_wraps_decode_errors(tmp_path: Path) -> None:
    path = tmp_path / "schema.csv"
    path.write_bytes(b"\xff\xfe")

    with pytest.raises(InputParseError, match="CSV_PARSE_FAILED"):
        CsvParser().parse(path)


def test_csv_parser_normalizes_blank_cells_to_json_null(tmp_path: Path) -> None:
    path = tmp_path / "schema.csv"
    path.write_text("name,description\nMaterial,\n", encoding="utf-8")

    document = CsvParser().parse(path)

    assert document.model_dump(mode="json") == {
        "path": str(path),
        "input_format": "csv",
        "sheets": [
            {
                "name": "data",
                "rows": [{"name": "Material", "description": None}],
            }
        ],
    }


@pytest.mark.parametrize(
    ("contents", "cause_type"),
    [(None, FileNotFoundError), (b"", pd.errors.EmptyDataError)],
    ids=["missing", "empty"],
)
def test_csv_parser_wraps_file_errors(
    tmp_path: Path,
    contents: bytes | None,
    cause_type: type[BaseException],
) -> None:
    path = tmp_path / "schema.csv"
    if contents is not None:
        path.write_bytes(contents)

    with pytest.raises(InputParseError) as exc_info:
        CsvParser().parse(path)

    error = exc_info.value
    assert error.code == "CSV_PARSE_FAILED"
    assert error.path == path
    assert error.detail
    assert isinstance(error.__cause__, cause_type)
    assert error.detail == str(error.__cause__)


def test_csv_parser_does_not_modify_input_bytes(tmp_path: Path) -> None:
    path = tmp_path / "schema.csv"
    original = b"name,data_type\r\nMaterial,string\r\n"
    path.write_bytes(original)

    CsvParser().parse(path)

    assert path.read_bytes() == original
