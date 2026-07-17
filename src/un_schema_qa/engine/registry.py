import re

from un_schema_qa.engine.protocols import Validator

RULE_CODE_PATTERN = re.compile(r"^UNQA-V[0-9]{3}$")


class ValidatorRegistry:
    def __init__(self) -> None:
        self._validators: dict[str, Validator] = {}

    def register(self, validator: Validator) -> None:
        if RULE_CODE_PATTERN.fullmatch(validator.code) is None:
            raise ValueError(f"invalid validator code {validator.code!r}")
        if validator.code in self._validators:
            raise ValueError(f"validator {validator.code!r} is already registered")
        self._validators[validator.code] = validator

    def get(self, code: str) -> Validator | None:
        return self._validators.get(code)

    def ordered(self) -> tuple[Validator, ...]:
        return tuple(self._validators[code] for code in sorted(self._validators))
