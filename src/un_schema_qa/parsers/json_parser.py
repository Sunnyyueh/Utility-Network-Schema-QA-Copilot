import json
from pathlib import Path
from typing import NoReturn

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import (
    InputParseError,
    ParsedDocument,
    document_from_structured_data,
)


class _NonStandardConstantError(ValueError):
    pass


def _reject_non_standard_constant(constant: str) -> NoReturn:
    raise _NonStandardConstantError(f"non-standard JSON constant: {constant}")


class JsonParser:
    def parse(self, path: Path) -> ParsedDocument:
        try:
            data = json.loads(
                path.read_text(encoding="utf-8"),
                parse_constant=_reject_non_standard_constant,
            )
        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            _NonStandardConstantError,
        ) as exc:
            raise InputParseError("JSON_PARSE_FAILED", path, str(exc)) from exc
        return document_from_structured_data(path, InputFormat.JSON, data)
