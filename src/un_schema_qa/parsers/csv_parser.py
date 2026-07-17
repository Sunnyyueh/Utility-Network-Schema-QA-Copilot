import csv
from pathlib import Path
from typing import Any, cast

import pandas as pd

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import InputParseError, ParsedDocument, ParsedSheet


class CsvParser:
    def parse(self, path: Path) -> ParsedDocument:
        try:
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.reader(stream, strict=True)
                header_missing = False
                try:
                    headers = tuple(next(reader))
                except StopIteration:
                    headers = ()
                    header_missing = True
        except (OSError, UnicodeError, csv.Error) as exc:
            raise InputParseError("CSV_PARSE_FAILED", path, str(exc)) from exc

        if not headers and not header_missing:
            raise InputParseError("CSV_PARSE_FAILED", path, "empty first CSV record")
        _validate_headers(path, headers)
        try:
            frame = pd.read_csv(
                path,
                dtype=object,
                encoding="utf-8-sig",
                header=0,
                names=headers or None,
            )
        except (
            OSError,
            UnicodeError,
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
        ) as exc:
            raise InputParseError("CSV_PARSE_FAILED", path, str(exc)) from exc
        normalized = frame.astype(object).where(pd.notna(frame), cast(Any, None))
        rows = tuple(
            {str(key): value for key, value in record.items()}
            for record in normalized.to_dict(orient="records")
        )
        return ParsedDocument(
            path=str(path),
            input_format=InputFormat.CSV,
            sheets=(ParsedSheet(name="data", rows=rows),),
        )


def _validate_headers(path: Path, headers: tuple[str, ...]) -> None:
    seen: set[str] = set()
    for column, header in enumerate(headers, start=1):
        if not header.strip():
            raise InputParseError(
                "CSV_PARSE_FAILED",
                path,
                f"blank header at column {column}",
            )
        if header in seen:
            raise InputParseError(
                "CSV_PARSE_FAILED",
                path,
                f"duplicate header {header!r}",
            )
        seen.add(header)
