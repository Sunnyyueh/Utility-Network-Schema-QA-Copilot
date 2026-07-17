from collections.abc import Mapping
from math import isfinite
from types import MappingProxyType
from typing import Annotated, cast

from pydantic import JsonValue as PydanticJsonValue
from pydantic import PlainSerializer, PlainValidator


def freeze_json_value(value: object) -> object:
    if value is None or type(value) in (bool, str, int):
        return value
    if type(value) is float:
        if not isfinite(value):
            raise ValueError("JSON numbers must be finite")
        return value
    if isinstance(value, (list, tuple)):
        return tuple(freeze_json_value(item) for item in value)
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise ValueError("JSON object keys must be strings")
        return MappingProxyType(
            {key: freeze_json_value(item) for key, item in value.items()}
        )
    raise ValueError("value must be JSON-compatible")


def freeze_json_object(value: object) -> object:
    if not isinstance(value, Mapping):
        raise ValueError("value must be a JSON object")
    return freeze_json_value(value)


def json_compatible(value: object) -> PydanticJsonValue:
    if value is None or isinstance(value, (bool, str, int, float)):
        return value
    if isinstance(value, tuple):
        return [json_compatible(item) for item in value]
    mapping = cast(Mapping[str, object], value)
    return {key: json_compatible(item) for key, item in mapping.items()}


def freeze_mapping[Key, Value](values: Mapping[Key, Value]) -> Mapping[Key, Value]:
    return MappingProxyType(dict(values))


FrozenJsonValue = Annotated[
    PydanticJsonValue,
    PlainValidator(
        freeze_json_value,
        json_schema_input_type=PydanticJsonValue,
    ),
    PlainSerializer(
        json_compatible,
        return_type=PydanticJsonValue,
        when_used="json",
    ),
]

FrozenJsonObject = Annotated[
    dict[str, PydanticJsonValue],
    PlainValidator(
        freeze_json_object,
        json_schema_input_type=dict[str, PydanticJsonValue],
    ),
    PlainSerializer(
        json_compatible,
        return_type=PydanticJsonValue,
        when_used="json",
    ),
]
