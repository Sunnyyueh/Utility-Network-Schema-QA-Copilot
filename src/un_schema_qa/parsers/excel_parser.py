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
            workbook = pd.read_excel(path, sheet_name=None, dtype=object)
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
