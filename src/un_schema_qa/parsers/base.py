from pathlib import Path
from typing import Any, Protocol, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    TypeAdapter,
    ValidationError,
)

from un_schema_qa.models.enums import InputFormat


class InputParseError(Exception):
    def __init__(self, code: str, path: Path, detail: str) -> None:
        self.code = code
        self.path = path
        self.detail = detail
        super().__init__(f"{code}: {path}: {detail}")


class ParsedSheet(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    rows: tuple[dict[str, JsonValue], ...] = ()


class ParsedDocument(BaseModel):
    model_config = ConfigDict(frozen=True)

    path: str
    input_format: InputFormat
    sheets: tuple[ParsedSheet, ...]


class Parser(Protocol):
    def parse(self, path: Path) -> ParsedDocument:
        """Parse one supported input document."""
        ...


_ROW_ADAPTER: TypeAdapter[dict[str, JsonValue]] = TypeAdapter(
    dict[str, JsonValue],
    config=ConfigDict(strict=True, allow_inf_nan=False),
)


def document_from_structured_data(
    path: Path,
    input_format: InputFormat,
    data: Any,
) -> ParsedDocument:
    sheets: tuple[ParsedSheet, ...]
    if isinstance(data, list):
        sheets = (ParsedSheet(name="data", rows=_validate_rows(path, "data", data)),)
    elif isinstance(data, dict):
        if any(not isinstance(name, str) or not name for name in data):
            raise InputParseError(
                "STRUCTURE_INVALID",
                path,
                "sheet names must be non-empty strings",
            )
        sheet_mapping = cast(dict[str, Any], data)
        sheets = tuple(
            ParsedSheet(name=name, rows=_validate_rows(path, name, rows))
            for name, rows in sorted(sheet_mapping.items())
        )
    else:
        raise InputParseError("STRUCTURE_INVALID", path, "expected a list or sheet mapping")
    return ParsedDocument(path=str(path), input_format=input_format, sheets=sheets)


def _validate_rows(
    path: Path,
    sheet: str,
    rows: Any,
) -> tuple[dict[str, JsonValue], ...]:
    if not isinstance(rows, list):
        raise InputParseError(
            "ROWS_INVALID",
            path,
            f"sheet {sheet!r} must contain a list of JSON-compatible objects",
        )

    try:
        return tuple(_ROW_ADAPTER.validate_python(row) for row in rows)
    except ValidationError as error:
        raise InputParseError(
            "ROWS_INVALID",
            path,
            f"sheet {sheet!r} must contain a list of JSON-compatible objects",
        ) from error
