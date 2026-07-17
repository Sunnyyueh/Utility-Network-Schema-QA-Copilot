from datetime import UTC, datetime

import pytest

from un_schema_qa.engine import ValidationEngine as PublicValidationEngine
from un_schema_qa.engine.registry import ValidatorRegistry
from un_schema_qa.engine.runner import ValidationEngine
from un_schema_qa.models.enums import CheckStatus, RunStatus, UtilityDomain
from un_schema_qa.models.profiles import UtilityProfile
from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.results import CheckResult, RunError


class PassingValidator:
    code = "UNQA-V001"
    rule_version = "1.0.0"

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        return (
            _result(
                finding_code=self.code,
                profile=project.profile.domain,
            ),
        )


class FailingValidator:
    code = "UNQA-V002"
    rule_version = "1.0.0"

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        raise RuntimeError("validator crashed")


class ReturningValidator:
    rule_version = "1.0.0"

    def __init__(self, code: str, results: tuple[CheckResult, ...]) -> None:
        self.code = code
        self._results = results

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        return self._results


class RaisingValidator:
    rule_version = "1.0.0"

    def __init__(self, code: str, error: BaseException) -> None:
        self.code = code
        self._error = error

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        raise self._error


class MalformedValidator:
    code = "UNQA-V002"
    rule_version = "1.0.0"

    def __init__(self, returned: object) -> None:
        self._returned = returned

    def validate(self, project: ValidationProject) -> object:
        return self._returned


def _project() -> ValidationProject:
    return ValidationProject(
        profile=UtilityProfile(
            name="Water Foundation",
            domain=UtilityDomain.WATER,
            version="1.0.0",
        ),
    )


def _result(**overrides: object) -> CheckResult:
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


def _engine(registry: ValidatorRegistry) -> ValidationEngine:
    return ValidationEngine(
        registry,
        clock=lambda: datetime(2026, 7, 16, tzinfo=UTC),
    )


def test_engine_preserves_results_when_one_validator_fails() -> None:
    registry = ValidatorRegistry()
    registry.register(FailingValidator())
    registry.register(PassingValidator())
    engine = ValidationEngine(
        registry,
        clock=lambda: datetime(2026, 7, 16, tzinfo=UTC),
    )
    project = _project()

    run = engine.run(project, run_id="run-001", ruleset_version="1.0.0")

    assert run.status is RunStatus.COMPLETED_WITH_ERRORS
    assert [result.finding_code for result in run.results] == ["UNQA-V001"]
    assert run.errors[0].component == "UNQA-V002"
    assert run.errors[0].recoverable is True


def test_engine_with_no_validators_is_completed() -> None:
    run = _engine(ValidatorRegistry()).run(
        _project(),
        run_id="run-001",
        ruleset_version="1.0.0",
    )

    assert run.status is RunStatus.COMPLETED
    assert run.results == ()
    assert run.errors == ()


def test_engine_with_all_successful_validators_is_completed() -> None:
    registry = ValidatorRegistry()
    registry.register(ReturningValidator("UNQA-V002", (_result(finding_code="UNQA-V002"),)))
    registry.register(ReturningValidator("UNQA-V001", (_result(finding_code="UNQA-V001"),)))

    run = _engine(registry).run(_project(), run_id="run-001", ruleset_version="1.0.0")

    assert run.status is RunStatus.COMPLETED
    assert [result.finding_code for result in run.results] == ["UNQA-V001", "UNQA-V002"]
    assert run.errors == ()


def test_engine_with_all_failed_validators_is_failed() -> None:
    registry = ValidatorRegistry()
    registry.register(RaisingValidator("UNQA-V001", RuntimeError("first")))
    registry.register(RaisingValidator("UNQA-V002", ValueError("second")))

    run = _engine(registry).run(_project(), run_id="run-001", ruleset_version="1.0.0")

    assert run.status is RunStatus.FAILED
    assert run.results == ()
    assert len(run.errors) == 2


def test_empty_success_plus_failure_is_completed_with_errors() -> None:
    registry = ValidatorRegistry()
    registry.register(ReturningValidator("UNQA-V001", ()))
    registry.register(RaisingValidator("UNQA-V002", RuntimeError("failed")))

    run = _engine(registry).run(_project(), run_id="run-001", ruleset_version="1.0.0")

    assert run.status is RunStatus.COMPLETED_WITH_ERRORS
    assert run.results == ()
    assert len(run.errors) == 1


def test_results_are_sorted_by_finding_code_dataset_field_and_domain() -> None:
    unsorted_results = (
        _result(finding_code="UNQA-V002"),
        _result(dataset="beta", field="field-a", domain="domain-a"),
        _result(dataset="alpha", field="field-b", domain="domain-a"),
        _result(dataset="alpha", field="field-a", domain="domain-b"),
        _result(dataset="alpha", field="field-a", domain="domain-a"),
        _result(dataset=None, field=None, domain=None),
    )
    registry = ValidatorRegistry()
    registry.register(ReturningValidator("UNQA-V001", unsorted_results))

    run = _engine(registry).run(_project(), run_id="run-001", ruleset_version="1.0.0")

    assert [
        (result.finding_code, result.dataset, result.field, result.domain)
        for result in run.results
    ] == [
        ("UNQA-V001", None, None, None),
        ("UNQA-V001", "alpha", "field-a", "domain-a"),
        ("UNQA-V001", "alpha", "field-a", "domain-b"),
        ("UNQA-V001", "alpha", "field-b", "domain-a"),
        ("UNQA-V001", "beta", "field-a", "domain-a"),
        ("UNQA-V002", None, None, None),
    ]


def test_errors_remain_in_registry_code_order() -> None:
    registry = ValidatorRegistry()
    registry.register(RaisingValidator("UNQA-V003", RuntimeError("third")))
    registry.register(RaisingValidator("UNQA-V001", RuntimeError("first")))
    registry.register(RaisingValidator("UNQA-V002", RuntimeError("second")))

    run = _engine(registry).run(_project(), run_id="run-001", ruleset_version="1.0.0")

    assert [error.component for error in run.errors] == [
        "UNQA-V001",
        "UNQA-V002",
        "UNQA-V003",
    ]
    assert [error.message for error in run.errors] == ["first", "second", "third"]


def test_metadata_uses_run_ruleset_profile_and_one_clock_call() -> None:
    started_at = datetime(2026, 7, 17, 12, 30, tzinfo=UTC)
    clock_calls = 0

    def clock() -> datetime:
        nonlocal clock_calls
        clock_calls += 1
        return started_at

    engine = ValidationEngine(ValidatorRegistry(), clock=clock)

    run = engine.run(_project(), run_id="run-023", ruleset_version="2.4.6")

    assert run.metadata.run_id == "run-023"
    assert run.metadata.ruleset_version == "2.4.6"
    assert run.metadata.profile_version == "1.0.0"
    assert run.metadata.started_at == started_at
    assert clock_calls == 1


def test_validator_failure_has_exact_recoverable_engine_error() -> None:
    registry = ValidatorRegistry()
    registry.register(FailingValidator())

    run = _engine(registry).run(_project(), run_id="run-001", ruleset_version="1.0.0")

    assert run.errors == (
        RunError(
            category="validator_execution",
            code="ENGINE_VALIDATOR_FAILURE",
            message="validator crashed",
            component="UNQA-V002",
            recoverable=True,
        ),
    )


@pytest.mark.parametrize("message", ["", "  \t\n"])
def test_empty_exception_message_uses_exception_class_fallback(message: str) -> None:
    registry = ValidatorRegistry()
    registry.register(RaisingValidator("UNQA-V001", RuntimeError(message)))

    run = _engine(registry).run(_project(), run_id="run-001", ruleset_version="1.0.0")

    assert run.errors[0].message == "RuntimeError"


@pytest.mark.parametrize(
    "returned",
    [
        [_result()],
        _result(),
        (_result(), object()),
    ],
)
def test_malformed_validator_output_is_isolated_without_result_leakage(
    returned: object,
) -> None:
    registry = ValidatorRegistry()
    registry.register(ReturningValidator("UNQA-V001", (_result(),)))
    registry.register(MalformedValidator(returned))

    run = _engine(registry).run(_project(), run_id="run-001", ruleset_version="1.0.0")

    assert run.status is RunStatus.COMPLETED_WITH_ERRORS
    assert len(run.results) == 1
    assert run.results[0].finding_code == "UNQA-V001"
    assert len(run.errors) == 1
    assert run.errors[0].category == "validator_execution"
    assert run.errors[0].code == "ENGINE_VALIDATOR_FAILURE"
    assert run.errors[0].component == "UNQA-V002"
    assert run.errors[0].recoverable is True


def test_base_exception_is_not_isolated() -> None:
    registry = ValidatorRegistry()
    registry.register(RaisingValidator("UNQA-V001", SystemExit("stop")))

    with pytest.raises(SystemExit, match="stop"):
        _engine(registry).run(_project(), run_id="run-001", ruleset_version="1.0.0")


def test_engine_package_re_exports_validation_engine() -> None:
    assert PublicValidationEngine is ValidationEngine
