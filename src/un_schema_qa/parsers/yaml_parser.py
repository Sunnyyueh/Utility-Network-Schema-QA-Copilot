from pathlib import Path

import yaml

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import (
    InputParseError,
    ParsedDocument,
    document_from_structured_data,
)


class YamlParser:
    def parse(self, path: Path) -> ParsedDocument:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise InputParseError("YAML_PARSE_FAILED", path, str(exc)) from exc
        return document_from_structured_data(path, InputFormat.YAML, data)
