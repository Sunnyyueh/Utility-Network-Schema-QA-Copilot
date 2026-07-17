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


def test_csv_parser_preserves_default_na_tokens_as_text(tmp_path: Path) -> None:
    path = tmp_path / "schema.csv"
    path.write_text(
        "text,blank\nNA,\nN/A,\nNULL,\nNaN,\n",
        encoding="utf-8",
    )

    document = CsvParser().parse(path)

    assert document.sheets[0].rows == (
        {"text": "NA", "blank": None},
        {"text": "N/A", "blank": None},
        {"text": "NULL", "blank": None},
        {"text": "NaN", "blank": None},
    )


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


def test_csv_parser_rejects_duplicate_raw_headers(tmp_path: Path) -> None:
    path = tmp_path / "schema.csv"
    path.write_text("name,name\nMaterial,PVC\n", encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        CsvParser().parse(path)

    error = exc_info.value
    assert error.code == "CSV_PARSE_FAILED"
    assert error.path == path
    assert error.detail == "duplicate header 'name'"


@pytest.mark.parametrize("header", ["name,", "name,   "])
def test_csv_parser_rejects_blank_or_missing_raw_headers(
    tmp_path: Path,
    header: str,
) -> None:
    path = tmp_path / "schema.csv"
    path.write_text(f"{header}\nMaterial,PVC\n", encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        CsvParser().parse(path)

    error = exc_info.value
    assert error.code == "CSV_PARSE_FAILED"
    assert error.path == path
    assert error.detail == "blank header at column 2"


def test_csv_parser_rejects_an_empty_first_record_before_pandas_skips_it(
    tmp_path: Path,
) -> None:
    path = tmp_path / "schema.csv"
    path.write_text("\nname,name\na,b\n", encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        CsvParser().parse(path)

    error = exc_info.value
    assert error.code == "CSV_PARSE_FAILED"
    assert error.path == path
    assert error.detail == "empty first CSV record"


def test_csv_parser_rejects_duplicate_after_pandas_bom_normalization(
    tmp_path: Path,
) -> None:
    path = tmp_path / "schema.csv"
    path.write_text("\ufeffname,name\na,b\n", encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        CsvParser().parse(path)

    error = exc_info.value
    assert error.code == "CSV_PARSE_FAILED"
    assert error.path == path
    assert error.detail == "duplicate header 'name'"


def test_csv_parser_accepts_a_single_utf8_bom_header(tmp_path: Path) -> None:
    path = tmp_path / "schema.csv"
    path.write_text("\ufeffname,data_type\nMaterial,string\n", encoding="utf-8")

    document = CsvParser().parse(path)

    assert document.sheets[0].rows == (
        {"name": "Material", "data_type": "string"},
    )


@pytest.mark.parametrize(
    ("row", "actual_fields"),
    [("x,y,z", 3), ("x", 1), ("", 0)],
    ids=["extra-field", "missing-field", "blank-record"],
)
def test_csv_parser_rejects_malformed_data_record_widths(
    tmp_path: Path,
    row: str,
    actual_fields: int,
) -> None:
    path = tmp_path / "schema.csv"
    path.write_text(f"a,b\n{row}\n", encoding="utf-8")

    with pytest.raises(InputParseError) as exc_info:
        CsvParser().parse(path)

    error = exc_info.value
    assert error.code == "CSV_PARSE_FAILED"
    assert error.path == path
    assert error.detail == (
        f"CSV record 2 has {actual_fields} fields; expected 2"
    )


def test_csv_parser_accepts_a_quoted_comma_field(tmp_path: Path) -> None:
    path = tmp_path / "schema.csv"
    path.write_text('a,b\n"x,y",z\n', encoding="utf-8")

    document = CsvParser().parse(path)

    assert document.sheets[0].rows == ({"a": "x,y", "b": "z"},)


def test_csv_parser_accepts_a_quoted_newline_field(tmp_path: Path) -> None:
    path = tmp_path / "schema.csv"
    path.write_text('a,b\n"x\ny",z\n', encoding="utf-8")

    document = CsvParser().parse(path)

    assert document.sheets[0].rows == ({"a": "x\ny", "b": "z"},)
