import pytest
from pydantic import ValidationError

from un_schema_qa.models.enums import CheckStatus, UtilityDomain
from un_schema_qa.models.profiles import RuleConfiguration, UtilityProfile


def test_profile_accepts_versioned_rule_configuration() -> None:
    profile = UtilityProfile(
        name="Water Foundation",
        domain=UtilityDomain.WATER,
        version="1.0.0",
        rule_configuration=RuleConfiguration(
            enabled_codes=("UNQA-V001", "UNQA-V017"),
            severity_overrides={"UNQA-V017": CheckStatus.WARNING},
        ),
    )

    assert profile.rule_configuration.enabled_codes == ("UNQA-V001", "UNQA-V017")


def test_profile_rejects_invalid_rule_codes() -> None:
    with pytest.raises(ValidationError):
        RuleConfiguration(enabled_codes=("INVALID",))


def test_rule_configuration_rejects_invalid_severity_override_code() -> None:
    with pytest.raises(ValidationError):
        RuleConfiguration(severity_overrides={"INVALID": CheckStatus.WARNING})


def test_rule_configuration_rejects_unicode_digit_rule_code() -> None:
    with pytest.raises(ValidationError):
        RuleConfiguration(enabled_codes=("UNQA-V\u0660\u0660\u0661",))


@pytest.mark.parametrize("version", ["1.0", "\u0661.0.0"])
def test_profile_rejects_invalid_version(version: str) -> None:
    with pytest.raises(ValidationError):
        UtilityProfile(
            name="Water Foundation",
            domain=UtilityDomain.WATER,
            version=version,
        )


def test_profile_rejects_empty_name() -> None:
    with pytest.raises(ValidationError):
        UtilityProfile(name="", domain=UtilityDomain.WATER, version="1.0.0")


def test_rule_configuration_serializes_status_override_in_json_mode() -> None:
    configuration = RuleConfiguration(
        severity_overrides={"UNQA-V017": CheckStatus.WARNING},
    )

    assert configuration.model_dump(mode="json")["severity_overrides"] == {
        "UNQA-V017": "warning"
    }


def test_profile_is_immutable() -> None:
    profile = UtilityProfile(
        name="Water Foundation",
        domain=UtilityDomain.WATER,
        version="1.0.0",
    )

    with pytest.raises(ValidationError) as error:
        profile.name = "Updated Profile"

    assert error.value.errors()[0]["type"] == "frozen_instance"
