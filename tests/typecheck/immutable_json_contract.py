from collections.abc import Mapping
from typing import assert_type

from un_schema_qa.models.json_values import ImmutableJsonValue
from un_schema_qa.models.results import CheckResult
from un_schema_qa.models.schema import FieldDefinition
from un_schema_qa.parsers.base import ParsedSheet


def assert_runtime_accurate_immutable_json_types(
    field: FieldDefinition,
    result: CheckResult,
    sheet: ParsedSheet,
) -> None:
    assert_type(field.default, ImmutableJsonValue)
    assert_type(result.expected, ImmutableJsonValue)
    assert_type(result.actual, ImmutableJsonValue)
    assert_type(result.evidence, Mapping[str, ImmutableJsonValue])
    assert_type(sheet.rows, tuple[Mapping[str, ImmutableJsonValue], ...])
