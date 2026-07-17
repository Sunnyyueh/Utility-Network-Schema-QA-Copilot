import pytest
from pydantic import ValidationError

from un_schema_qa.models.common import SourceLocation


def test_source_location_serializes_only_supplied_coordinates() -> None:
    location = SourceLocation(file="schema.xlsx", sheet="Fields", row=4, column="name")

    assert location.model_dump(exclude_none=True) == {
        "file": "schema.xlsx",
        "sheet": "Fields",
        "row": 4,
        "column": "name",
    }


def test_source_location_omits_unsupplied_optional_coordinates() -> None:
    location = SourceLocation(file="schema.csv")

    assert location.model_dump(exclude_none=True) == {"file": "schema.csv"}


def test_source_location_rejects_zero_based_rows() -> None:
    with pytest.raises(ValidationError):
        SourceLocation(file="schema.csv", row=0)


def test_source_location_is_immutable() -> None:
    location = SourceLocation(file="schema.csv", row=1)

    with pytest.raises(ValidationError) as error:
        location.row = 2

    assert error.value.errors()[0]["type"] == "frozen_instance"
