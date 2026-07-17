from typing import Protocol, runtime_checkable

from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.results import CheckResult


@runtime_checkable
class Validator(Protocol):
    code: str
    rule_version: str

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        """Return deterministic check results for one rule."""
        ...
