import pytest

from un_schema_qa.engine.registry import ValidatorRegistry
from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.results import CheckResult


class StubValidator:
    def __init__(self, code: str) -> None:
        self.code = code
        self.rule_version = "1.0.0"

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        return ()


def test_registry_returns_validators_in_code_order() -> None:
    registry = ValidatorRegistry()
    registry.register(StubValidator("UNQA-V002"))
    registry.register(StubValidator("UNQA-V001"))
    assert [validator.code for validator in registry.ordered()] == [
        "UNQA-V001",
        "UNQA-V002",
    ]


def test_registry_rejects_duplicate_codes() -> None:
    registry = ValidatorRegistry()
    registry.register(StubValidator("UNQA-V001"))
    with pytest.raises(ValueError, match="already registered"):
        registry.register(StubValidator("UNQA-V001"))


def test_registry_get_returns_registered_validator() -> None:
    registry = ValidatorRegistry()
    validator = StubValidator("UNQA-V001")
    registry.register(validator)

    assert registry.get("UNQA-V001") is validator


def test_registry_get_returns_none_for_missing_code() -> None:
    assert ValidatorRegistry().get("UNQA-V001") is None


def test_registry_ordered_is_an_empty_tuple_when_no_validators_are_registered() -> None:
    assert ValidatorRegistry().ordered() == ()


@pytest.mark.parametrize(
    "code",
    [
        "UNQA-V01",
        "UNQA-V0001",
        "unqa-v001",
        "UNQA-VABC",
        " UNQA-V001",
        "UNQA-V001 ",
        "UNQA-V\u0660\u0660\u0661",
        "UNQA-V\uff10\uff10\uff11",
    ],
)
def test_registry_rejects_invalid_code_formats(code: str) -> None:
    registry = ValidatorRegistry()

    with pytest.raises(ValueError, match="invalid validator code"):
        registry.register(StubValidator(code))


def test_registry_ordered_preserves_validator_identity_in_a_tuple_snapshot() -> None:
    registry = ValidatorRegistry()
    second = StubValidator("UNQA-V002")
    registry.register(second)

    snapshot = registry.ordered()
    registry.register(StubValidator("UNQA-V001"))

    assert snapshot == (second,)
    assert registry.ordered()[1] is second


def test_duplicate_registration_leaves_original_validator_intact() -> None:
    registry = ValidatorRegistry()
    original = StubValidator("UNQA-V001")
    registry.register(original)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(StubValidator("UNQA-V001"))

    assert registry.get("UNQA-V001") is original
