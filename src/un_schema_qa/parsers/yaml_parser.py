from pathlib import Path

import yaml
from yaml.nodes import MappingNode

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import (
    InputParseError,
    ParsedDocument,
    document_from_structured_data,
)


class _DuplicateKeyError(yaml.YAMLError):
    pass


class _UniqueKeySafeLoader(yaml.SafeLoader):
    def construct_mapping(
        self,
        node: MappingNode,
        deep: bool = False,
    ) -> dict[object, object]:
        self.flatten_mapping(node)
        result: dict[object, object] = {}
        for key, value in self.construct_pairs(node, deep=deep):
            if key in result:
                raise _DuplicateKeyError(f"duplicate key {key!r}")
            result[key] = value
        return result


class YamlParser:
    def parse(self, path: Path) -> ParsedDocument:
        try:
            data = yaml.load(
                path.read_text(encoding="utf-8"),
                Loader=_UniqueKeySafeLoader,
            )
        except (OSError, UnicodeError, TypeError, yaml.YAMLError) as exc:
            raise InputParseError("YAML_PARSE_FAILED", path, str(exc)) from exc
        return document_from_structured_data(path, InputFormat.YAML, data)
