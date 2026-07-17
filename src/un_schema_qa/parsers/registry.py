from pathlib import Path

from un_schema_qa.parsers.base import InputParseError, ParsedDocument, Parser
from un_schema_qa.parsers.csv_parser import CsvParser
from un_schema_qa.parsers.excel_parser import ExcelParser
from un_schema_qa.parsers.json_parser import JsonParser
from un_schema_qa.parsers.yaml_parser import YamlParser


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: dict[str, Parser] = {}

    def register(self, suffix: str, parser: Parser) -> None:
        self._parsers[suffix.casefold()] = parser

    def parse(self, path: Path) -> ParsedDocument:
        parser = self._parsers.get(path.suffix.casefold())
        if parser is None:
            raise InputParseError(
                "FORMAT_UNSUPPORTED",
                path,
                f"unsupported suffix {path.suffix!r}",
            )
        return parser.parse(path)


DEFAULT_REGISTRY = ParserRegistry()
DEFAULT_REGISTRY.register(".csv", CsvParser())
DEFAULT_REGISTRY.register(".xlsx", ExcelParser())
DEFAULT_REGISTRY.register(".json", JsonParser())
DEFAULT_REGISTRY.register(".yaml", YamlParser())
DEFAULT_REGISTRY.register(".yml", YamlParser())


def parse_document(path: Path) -> ParsedDocument:
    return DEFAULT_REGISTRY.parse(path)
