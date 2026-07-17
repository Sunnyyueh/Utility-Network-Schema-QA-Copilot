import pytest

from un_schema_qa.engine.protocols import Validator
from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.results import CheckResult


class ExampleValidator:
    code = "UNQA-V001"
    rule_version = "1.0.0"

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        return ()


class ValidatorWithoutCode:
    rule_version = "1.0.0"

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        return ()


class ValidatorWithoutRuleVersion:
    code = "UNQA-V001"

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        return ()


class ValidatorWithoutValidate:
    code = "UNQA-V001"
    rule_version = "1.0.0"


class ValidatorWithNonCallableValidate:
    code = "UNQA-V001"
    rule_version = "1.0.0"
    validate = None


def test_validator_protocol_accepts_matching_implementation() -> None:
    validator = ExampleValidator()

    assert isinstance(validator, Validator)
    assert validator.validate(ValidationProject.model_construct()) == ()


@pytest.mark.parametrize(
    "candidate",
    (
        ValidatorWithoutCode(),
        ValidatorWithoutRuleVersion(),
        ValidatorWithoutValidate(),
        ValidatorWithNonCallableValidate(),
    ),
)
def test_validator_protocol_rejects_incomplete_implementations(candidate: object) -> None:
    assert not isinstance(candidate, Validator)
