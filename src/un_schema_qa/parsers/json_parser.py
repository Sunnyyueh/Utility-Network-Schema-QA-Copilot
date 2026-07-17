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


class _DuplicateKeyError(ValueError):
    pass


def _reject_non_standard_constant(constant: str) -> NoReturn:
    raise _NonStandardConstantError(f"non-standard JSON constant: {constant}")


def _object_without_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(f"duplicate key {key!r}")
        result[key] = value
    return result


class JsonParser:
    def parse(self, path: Path) -> ParsedDocument:
        try:
            data = json.loads(
                path.read_text(encoding="utf-8"),
                parse_constant=_reject_non_standard_constant,
                object_pairs_hook=_object_without_duplicates,
            )
        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            _NonStandardConstantError,
            _DuplicateKeyError,
        ) as exc:
            raise InputParseError("JSON_PARSE_FAILED", path, str(exc)) from exc
        return document_from_structured_data(path, InputFormat.JSON, data)
