from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from un_schema_qa.models.common import SourceLocation
from un_schema_qa.models.enums import CheckStatus, RunStatus, UtilityDomain
from un_schema_qa.models.results import CheckResult, RunError, RunMetadata, ValidationRun


def _check_result(**overrides: object) -> CheckResult:
    values: dict[str, object] = {
        "finding_code": "UNQA-V001",
        "rule_version": "1.0.0",
        "status": CheckStatus.PASS,
        "severity_rank": 0,
        "profile": UtilityDomain.WATER,
        "expected": {"required": ["name"]},
        "actual": {"present": ["name"]},
        "evidence": {"columns": ["name"]},
        "remediation_category": "none",
        "remediation_guidance": "No action required.",
    }
    values.update(overrides)
    return CheckResult.model_validate(values)


def _run_metadata(**overrides: object) -> RunMetadata:
    values: dict[str, object] = {
        "run_id": "run-001",
        "started_at": datetime(2026, 7, 16, tzinfo=UTC),
        "ruleset_version": "1.0.0",
        "profile_version": "1.0.0",
    }
    values.update(overrides)
    return RunMetadata.model_validate(values)


def test_validation_run_serializes_a_complete_result() -> None:
    result = _check_result()
    run = ValidationRun(
        metadata=_run_metadata(),
        status=RunStatus.COMPLETED,
        results=(result,),
    )

    assert run.model_dump(mode="json") == {
        "metadata": {
            "run_id": "run-001",
            "started_at": "2026-07-16T00:00:00Z",
            "ruleset_version": "1.0.0",
            "profile_version": "1.0.0",
        },
        "status": "completed",
        "results": [
            {
                "finding_code": "UNQA-V001",
                "rule_version": "1.0.0",
                "status": "pass",
                "severity_rank": 0,
                "profile": "water",
                "dataset": None,
                "field": None,
                "domain": None,
                "source_location": None,
                "expected": {"required": ["name"]},
                "actual": {"present": ["name"]},
                "evidence": {"columns": ["name"]},
                "remediation_category": "none",
                "remediation_guidance": "No action required.",
            }
        ],
        "errors": [],
    }


def test_run_error_serializes_runtime_failure_details() -> None:
    error = RunError(
        category="input",
        code="UNQA-E001",
        message="Workbook could not be opened.",
        component="xlsx-reader",
        recoverable=False,
        source_location=SourceLocation(file="schema.xlsx", sheet="Fields"),
    )

    assert error.model_dump(mode="json") == {
        "category": "input",
        "code": "UNQA-E001",
        "message": "Workbook could not be opened.",
        "component": "xlsx-reader",
        "recoverable": False,
        "source_location": {
            "file": "schema.xlsx",
            "sheet": "Fields",
            "row": None,
            "column": None,
        },
    }


def test_check_result_rejects_unicode_digits_in_finding_code() -> None:
    with pytest.raises(ValidationError):
        _check_result(finding_code="UNQA-V\u0660\u0660\u0661")


@pytest.mark.parametrize(
    ("model_name", "field_name"),
    [
        ("check_result", "rule_version"),
        ("run_metadata", "ruleset_version"),
        ("run_metadata", "profile_version"),
    ],
)
def test_result_models_reject_unicode_digits_in_versions(
    model_name: str, field_name: str
) -> None:
    overrides = {field_name: "\u0661.0.0"}

    with pytest.raises(ValidationError):
        if model_name == "check_result":
            _check_result(**overrides)
        else:
            _run_metadata(**overrides)


@pytest.mark.parametrize("severity_rank", [-1, 101])
def test_check_result_rejects_severity_rank_outside_bounds(severity_rank: int) -> None:
    with pytest.raises(ValidationError):
        _check_result(severity_rank=severity_rank)


@pytest.mark.parametrize("field_name", ["remediation_category", "remediation_guidance"])
def test_check_result_rejects_empty_remediation_text(field_name: str) -> None:
    with pytest.raises(ValidationError):
        _check_result(**{field_name: ""})


@pytest.mark.parametrize("field_name", ["category", "code", "message", "component"])
def test_run_error_rejects_empty_required_text(field_name: str) -> None:
    values: dict[str, object] = {
        "category": "input",
        "code": "UNQA-E001",
        "message": "Workbook could not be opened.",
        "component": "xlsx-reader",
        "recoverable": False,
    }
    values[field_name] = ""

    with pytest.raises(ValidationError):
        RunError.model_validate(values)


def test_check_result_rejects_non_json_values() -> None:
    with pytest.raises(ValidationError):
        _check_result(expected=object())


@pytest.mark.parametrize("field_name", ["expected", "actual", "evidence"])
@pytest.mark.parametrize(
    "value",
    [float("nan"), float("inf"), float("-inf"), {"nested": [float("inf")]}],
    ids=["nan", "positive-infinity", "negative-infinity", "nested-infinity"],
)
def test_check_result_json_fields_reject_non_finite_values(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(ValidationError):
        _check_result(**{field_name: value})


def test_check_result_json_fields_are_copied_deeply_frozen_and_serializable() -> None:
    expected = {"required": ["name"]}
    actual = {"present": ["name"]}
    evidence = {"columns": [{"name": "name", "confidence": 1.0}]}
    result = _check_result(expected=expected, actual=actual, evidence=evidence)

    expected["required"].append("type")
    actual["present"][0] = "changed"
    evidence["columns"][0]["confidence"] = 0.0

    assert result.expected == {"required": ("name",)}
    assert result.actual == {"present": ("name",)}
    assert result.evidence == {
        "columns": ({"name": "name", "confidence": 1.0},)
    }
    with pytest.raises(TypeError):
        result.evidence["columns"][0]["confidence"] = 0.5
    with pytest.raises(TypeError):
        result.evidence["columns"][0] = {"name": "other"}

    payload = result.model_dump(mode="json")
    assert payload["expected"] == {"required": ["name"]}
    assert payload["actual"] == {"present": ["name"]}
    assert payload["evidence"] == {
        "columns": [{"name": "name", "confidence": 1.0}]
    }
    assert '"columns":[{"name":"name","confidence":1.0}]' in result.model_dump_json()


def test_check_result_rejects_cyclic_json_input_as_validation_error() -> None:
    cyclic: dict[str, object] = {}
    cyclic["self"] = cyclic

    with pytest.raises(ValidationError, match="cyclic JSON value"):
        _check_result(expected=cyclic)


def test_check_result_accepts_repeated_shared_acyclic_json_input() -> None:
    shared = {"values": [1, 2]}

    result = _check_result(expected={"left": shared, "right": shared})

    assert result.model_dump(mode="json")["expected"] == {
        "left": {"values": [1, 2]},
        "right": {"values": [1, 2]},
    }


def test_check_result_json_schema_retains_json_input_contract() -> None:
    properties = CheckResult.model_json_schema()["properties"]

    assert properties["expected"]["$ref"] == "#/$defs/JsonValue"
    assert properties["actual"]["$ref"] == "#/$defs/JsonValue"
    assert properties["evidence"] == {
        "additionalProperties": {"$ref": "#/$defs/JsonValue"},
        "title": "Evidence",
        "type": "object",
    }


def test_validation_run_defaults_results_and_errors_to_tuples() -> None:
    run = ValidationRun(metadata=_run_metadata(), status=RunStatus.COMPLETED)

    assert run.results == ()
    assert run.errors == ()


def test_validation_run_is_immutable() -> None:
    run = ValidationRun(metadata=_run_metadata(), status=RunStatus.COMPLETED)

    with pytest.raises(ValidationError) as error:
        run.status = RunStatus.FAILED

    assert error.value.errors()[0]["type"] == "frozen_instance"
