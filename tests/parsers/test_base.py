from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import (
    InputParseError,
    ParsedDocument,
    ParsedSheet,
    document_from_structured_data,
)


def test_structured_list_becomes_a_default_sheet() -> None:
    document = document_from_structured_data(
        path=Path("schema.json"),
        input_format=InputFormat.JSON,
        data=[{"name": "Material"}],
    )

    assert document.sheets[0].name == "data"
    assert document.sheets[0].rows == ({"name": "Material"},)


def test_structured_mapping_becomes_named_sheets() -> None:
    document = document_from_structured_data(
        path=Path("schema.yaml"),
        input_format=InputFormat.YAML,
        data={"fields": [{"name": "Material"}], "domains": []},
    )

    assert [sheet.name for sheet in document.sheets] == ["domains", "fields"]


def test_structured_scalar_is_rejected() -> None:
    with pytest.raises(InputParseError, match="STRUCTURE_INVALID"):
        document_from_structured_data(
            path=Path("schema.json"),
            input_format=InputFormat.JSON,
            data="not-a-table",
        )


@pytest.mark.parametrize("rows", [{}, ["not-an-object"]])
def test_invalid_sheet_rows_raise_a_parser_error(rows: Any) -> None:
    with pytest.raises(InputParseError, match="ROWS_INVALID"):
        document_from_structured_data(
            path=Path("schema.yaml"),
            input_format=InputFormat.YAML,
            data={"fields": rows},
        )


@pytest.mark.parametrize("sheet_name", [1, ""])
def test_sheet_names_must_be_non_empty_strings(sheet_name: Any) -> None:
    with pytest.raises(InputParseError, match="STRUCTURE_INVALID"):
        document_from_structured_data(
            path=Path("schema.json"),
            input_format=InputFormat.JSON,
            data={sheet_name: []},
        )


@pytest.mark.parametrize("value", [object(), float("nan")])
def test_rows_reject_non_json_values(value: object) -> None:
    with pytest.raises(InputParseError, match="ROWS_INVALID"):
        document_from_structured_data(
            path=Path("schema.json"),
            input_format=InputFormat.JSON,
            data=[{"value": value}],
        )


def test_input_parse_error_exposes_stable_context() -> None:
    path = Path("schema.json")
    error = InputParseError("STRUCTURE_INVALID", path, "expected a list")

    assert error.code == "STRUCTURE_INVALID"
    assert error.path == path
    assert error.detail == "expected a list"
    assert str(error) == "STRUCTURE_INVALID: schema.json: expected a list"


def test_parsed_contracts_are_immutable() -> None:
    sheet = ParsedSheet(name="data")
    document = ParsedDocument(
        path="schema.json",
        input_format=InputFormat.JSON,
        sheets=(sheet,),
    )

    with pytest.raises(ValidationError) as sheet_error:
        sheet.name = "renamed"
    with pytest.raises(ValidationError) as document_error:
        document.path = "renamed.json"

    assert sheet_error.value.errors()[0]["type"] == "frozen_instance"
    assert document_error.value.errors()[0]["type"] == "frozen_instance"


def test_empty_list_becomes_an_empty_default_sheet() -> None:
    document = document_from_structured_data(
        path=Path("schema.json"),
        input_format=InputFormat.JSON,
        data=[],
    )

    assert document.sheets == (ParsedSheet(name="data"),)


def test_document_serializes_path_and_input_format_in_json_mode() -> None:
    document = document_from_structured_data(
        path=Path("schema.json"),
        input_format=InputFormat.JSON,
        data=[],
    )

    assert document.model_dump(mode="json") == {
        "path": "schema.json",
        "input_format": "json",
        "sheets": [{"name": "data", "rows": []}],
    }


def test_direct_parsed_sheet_rows_use_finite_deeply_frozen_json_values() -> None:
    original = {"attributes": [{"ratio": 1.5}]}
    sheet = ParsedSheet(name="data", rows=(original,))

    original["attributes"][0]["ratio"] = 9.5
    original["attributes"].append({"ratio": 2.5})

    assert sheet.rows == ({"attributes": ({"ratio": 1.5},)},)
    with pytest.raises(TypeError):
        sheet.rows[0]["attributes"][0]["ratio"] = 0.0
    with pytest.raises(TypeError):
        sheet.rows[0]["attributes"][0] = {"ratio": 0.0}
    assert sheet.model_dump(mode="json") == {
        "name": "data",
        "rows": [{"attributes": [{"ratio": 1.5}]}],
    }


@pytest.mark.parametrize(
    "row",
    [
        {"value": object()},
        {"value": float("nan")},
        {"value": float("inf")},
        {"value": float("-inf")},
        {"value": {1: "not-a-string-key"}},
    ],
    ids=["object", "nan", "positive-infinity", "negative-infinity", "non-string-key"],
)
def test_direct_parsed_sheet_rejects_values_outside_finite_json(row: object) -> None:
    with pytest.raises(ValidationError):
        ParsedSheet(name="data", rows=(row,))
