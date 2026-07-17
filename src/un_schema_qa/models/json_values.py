from collections.abc import Mapping
from math import isfinite
from types import MappingProxyType
from typing import Annotated, cast

from pydantic import JsonValue as PydanticJsonValue
from pydantic import PlainSerializer, PlainValidator

type ImmutableJsonScalar = None | bool | str | int | float
type ImmutableJsonValue = (
    ImmutableJsonScalar
    | tuple[ImmutableJsonValue, ...]
    | Mapping[str, ImmutableJsonValue]
)


def freeze_json_value(value: object) -> ImmutableJsonValue:
    return _freeze_json_value(value, set())


def _freeze_json_value(value: object, active: set[int]) -> ImmutableJsonValue:
    if value is None or type(value) in (bool, str, int):
        return cast(ImmutableJsonScalar, value)
    if type(value) is float:
        if not isfinite(value):
            raise ValueError("JSON numbers must be finite")
        return value
    if isinstance(value, (list, tuple, Mapping)):
        identity = id(value)
        if identity in active:
            raise ValueError("cyclic JSON value is not allowed")
        active.add(identity)
        try:
            if isinstance(value, (list, tuple)):
                return tuple(_freeze_json_value(item, active) for item in value)
            mapping = cast(Mapping[object, object], value)
            if any(type(key) is not str for key in mapping):
                raise ValueError("JSON object keys must be strings")
            return MappingProxyType(
                {
                    cast(str, key): _freeze_json_value(item, active)
                    for key, item in mapping.items()
                }
            )
        finally:
            active.remove(identity)
    raise ValueError("value must be JSON-compatible")


def freeze_json_object(value: object) -> Mapping[str, ImmutableJsonValue]:
    if not isinstance(value, Mapping):
        raise ValueError("value must be a JSON object")
    return cast(Mapping[str, ImmutableJsonValue], freeze_json_value(value))


def json_compatible(value: ImmutableJsonValue) -> PydanticJsonValue:
    if value is None or isinstance(value, (bool, str, int, float)):
        return value
    if isinstance(value, tuple):
        return [json_compatible(item) for item in value]
    return {key: json_compatible(item) for key, item in value.items()}


def freeze_mapping[Key, Value](values: Mapping[Key, Value]) -> Mapping[Key, Value]:
    return MappingProxyType(dict(values))


FrozenJsonValue = Annotated[
    ImmutableJsonValue,
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
    Mapping[str, ImmutableJsonValue],
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
