from enum import Enum


class CheckStatus(str, Enum):  # noqa: UP042
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    BLOCKER = "blocker"


class RunStatus(str, Enum):  # noqa: UP042
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"


class UtilityDomain(str, Enum):  # noqa: UP042
    WATER = "water"
    WASTEWATER = "wastewater"
    STORMWATER = "stormwater"


class InputFormat(str, Enum):  # noqa: UP042
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"
    YAML = "yaml"
