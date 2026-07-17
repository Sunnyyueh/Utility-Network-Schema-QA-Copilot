from collections.abc import Callable
from datetime import UTC, datetime

from un_schema_qa.engine.registry import ValidatorRegistry
from un_schema_qa.models.enums import RunStatus
from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.results import CheckResult, RunError, RunMetadata, ValidationRun


class ValidationEngine:
    def __init__(
        self,
        registry: ValidatorRegistry,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._registry = registry
        self._clock = clock or (lambda: datetime.now(UTC))

    def run(
        self,
        project: ValidationProject,
        run_id: str,
        ruleset_version: str,
    ) -> ValidationRun:
        results: list[CheckResult] = []
        errors: list[RunError] = []
        succeeded = 0
        validators = self._registry.ordered()

        for validator in validators:
            try:
                validator_results = validator.validate(project)
                if not isinstance(validator_results, tuple):
                    raise TypeError("validator results must be a tuple")
                if any(not isinstance(result, CheckResult) for result in validator_results):
                    raise TypeError("validator results must contain only CheckResult instances")
                results.extend(validator_results)
                succeeded += 1
            except Exception as exc:
                message = str(exc)
                if not message.strip():
                    message = type(exc).__name__
                errors.append(
                    RunError(
                        category="validator_execution",
                        code="ENGINE_VALIDATOR_FAILURE",
                        message=message,
                        component=validator.code,
                        recoverable=True,
                    )
                )

        if errors and validators and succeeded == 0:
            status = RunStatus.FAILED
        elif errors:
            status = RunStatus.COMPLETED_WITH_ERRORS
        else:
            status = RunStatus.COMPLETED

        ordered_results = tuple(
            sorted(
                results,
                key=lambda result: (
                    result.finding_code,
                    result.dataset or "",
                    result.field or "",
                    result.domain or "",
                ),
            )
        )
        return ValidationRun(
            metadata=RunMetadata(
                run_id=run_id,
                started_at=self._clock(),
                ruleset_version=ruleset_version,
                profile_version=project.profile.version,
            ),
            status=status,
            results=ordered_results,
            errors=tuple(errors),
        )
