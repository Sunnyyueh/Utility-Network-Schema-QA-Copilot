from pathlib import Path
from typing import Any, cast

import pandas as pd

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import (
    InputParseError,
    ParsedDocument,
    document_from_structured_data,
)


class ExcelParser:
    def parse(self, path: Path) -> ParsedDocument:
        try:
            raw_workbook = pd.read_excel(
                path,
                sheet_name=None,
                header=None,
                keep_default_na=False,
                na_values=[""],
                nrows=1,
                dtype=object,
            )
            for name, frame in raw_workbook.items():
                _validate_headers(path, name, frame)
            workbook = pd.read_excel(
                path,
                sheet_name=None,
                dtype=object,
                keep_default_na=False,
                na_values=[""],
            )
        except (OSError, ValueError) as exc:
            raise InputParseError("XLSX_PARSE_FAILED", path, str(exc)) from exc

        sheets = {
            name: [
                {str(key): value for key, value in record.items()}
                for record in frame.astype(object)
                .where(pd.notna(frame), cast(Any, None))
                .to_dict(orient="records")
            ]
            for name, frame in workbook.items()
        }
        return document_from_structured_data(path, InputFormat.XLSX, sheets)


def _validate_headers(path: Path, sheet: str, raw_frame: pd.DataFrame) -> None:
    if raw_frame.empty:
        raise InputParseError(
            "XLSX_PARSE_FAILED",
            path,
            f"worksheet {sheet!r}: missing header row",
        )

    seen: set[str] = set()
    for column, header in enumerate(raw_frame.iloc[0].tolist(), start=1):
        if pd.isna(header) or (isinstance(header, str) and not header.strip()):
            raise InputParseError(
                "XLSX_PARSE_FAILED",
                path,
                f"worksheet {sheet!r}: blank header at column {column}",
            )
        normalized = str(header)
        if normalized in seen:
            raise InputParseError(
                "XLSX_PARSE_FAILED",
                path,
                f"worksheet {sheet!r}: duplicate header {normalized!r}",
            )
        seen.add(normalized)
