import re
from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from un_schema_qa.models.enums import CheckStatus, UtilityDomain
from un_schema_qa.models.json_values import freeze_mapping

RULE_CODE_PATTERN = re.compile(r"^UNQA-V[0-9]{3}$")


class RuleConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True, validate_default=True)

    enabled_codes: tuple[str, ...] = ()
    severity_overrides: Mapping[str, CheckStatus] = Field(default_factory=dict)

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
        values: Mapping[str, CheckStatus],
    ) -> Mapping[str, CheckStatus]:
        if any(RULE_CODE_PATTERN.fullmatch(value) is None for value in values):
            raise ValueError("severity_overrides keys must use UNQA-V### format")
        return freeze_mapping(values)

    @field_serializer("severity_overrides")
    def serialize_severity_overrides(
        self,
        values: Mapping[str, CheckStatus],
    ) -> dict[str, CheckStatus]:
        return dict(values)


class UtilityProfile(BaseModel):
    model_config = ConfigDict(frozen=True, validate_default=True)

    name: str = Field(min_length=1)
    domain: UtilityDomain
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    terminology: Mapping[str, str] = Field(default_factory=dict)
    expected_asset_categories: tuple[str, ...] = ()
    classification_constraints: Mapping[str, tuple[str, ...]] = Field(default_factory=dict)
    rule_configuration: RuleConfiguration = Field(default_factory=RuleConfiguration)

    @field_validator("terminology")
    @classmethod
    def freeze_terminology(
        cls,
        values: Mapping[str, str],
    ) -> Mapping[str, str]:
        return freeze_mapping(values)

    @field_validator("classification_constraints")
    @classmethod
    def freeze_classification_constraints(
        cls,
        values: Mapping[str, tuple[str, ...]],
    ) -> Mapping[str, tuple[str, ...]]:
        return freeze_mapping(values)

    @field_serializer("terminology")
    def serialize_terminology(self, values: Mapping[str, str]) -> dict[str, str]:
        return dict(values)

    @field_serializer("classification_constraints")
    def serialize_classification_constraints(
        self,
        values: Mapping[str, tuple[str, ...]],
    ) -> dict[str, tuple[str, ...]]:
        return dict(values)
