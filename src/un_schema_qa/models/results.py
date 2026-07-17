from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from un_schema_qa.models.common import SourceLocation
from un_schema_qa.models.enums import CheckStatus, RunStatus, UtilityDomain
from un_schema_qa.models.json_values import FrozenJsonObject, FrozenJsonValue


class CheckResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    finding_code: str = Field(pattern=r"^UNQA-V[0-9]{3}$")
    rule_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    status: CheckStatus
    severity_rank: int = Field(ge=0, le=100)
    profile: UtilityDomain
    dataset: str | None = None
    field: str | None = None
    domain: str | None = None
    source_location: SourceLocation | None = None
    expected: FrozenJsonValue
    actual: FrozenJsonValue
    evidence: FrozenJsonObject
    remediation_category: str = Field(min_length=1)
    remediation_guidance: str = Field(min_length=1)


class RunError(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: str = Field(min_length=1)
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    component: str = Field(min_length=1)
    recoverable: bool
    source_location: SourceLocation | None = None


class RunMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str = Field(min_length=1)
    started_at: datetime
    ruleset_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    profile_version: str = Field(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")


class ValidationRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    metadata: RunMetadata
    status: RunStatus
    results: tuple[CheckResult, ...] = ()
    errors: tuple[RunError, ...] = ()
