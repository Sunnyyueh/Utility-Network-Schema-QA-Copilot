import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from un_schema_qa.models.enums import CheckStatus, UtilityDomain

RULE_CODE_PATTERN = re.compile(r"^UNQA-V[0-9]{3}$")


class RuleConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    enabled_codes: tuple[str, ...] = ()
    severity_overrides: dict[str, CheckStatus] = Field(default_factory=dict)

    @field_validator("enabled_codes")
    @classmethod
    def validate_enabled_codes(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if any(RULE_CODE_PATTERN.fullmatch(value) is None for value in values):
            raise ValueError("enabled_codes must use UNQA-V### format")
        return values

    @field_validator("severity_overrides")
    @classmethod
    def validate_override_codes(
        cls,
        values: dict[str, CheckStatus],
    ) -> dict[str, CheckStatus]:
        if any(RULE_CODE_PATTERN.fullmatch(value) is None for value in values):
            raise ValueError("severity_overrides keys must use UNQA-V### format")
        return values


class UtilityProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    domain: UtilityDomain
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    terminology: dict[str, str] = Field(default_factory=dict)
    expected_asset_categories: tuple[str, ...] = ()
    classification_constraints: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    rule_configuration: RuleConfiguration = Field(default_factory=RuleConfiguration)
