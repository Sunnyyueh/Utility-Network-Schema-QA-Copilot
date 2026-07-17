import pytest
from pydantic import ValidationError

from un_schema_qa.models.common import SourceLocation
from un_schema_qa.models.schema import DatasetDefinition, FieldDefinition


def test_dataset_resolves_a_field_case_insensitively() -> None:
    field = FieldDefinition(
        name="Material",
        data_type="string",
        required=True,
        nullable=False,
        length=50,
        source_location=SourceLocation(file="source.csv", row=2),
    )
    dataset = DatasetDefinition(name="WaterLine", fields=(field,))

    assert dataset.get_field("material") == field


def test_dataset_returns_none_for_unknown_field() -> None:
    dataset = DatasetDefinition(name="WaterLine")

    assert dataset.get_field("diameter") is None


@pytest.mark.parametrize("field_name,data_type", [("", "string"), ("Material", "")])
def test_field_rejects_empty_names_and_data_types(field_name: str, data_type: str) -> None:
    with pytest.raises(ValidationError):
        FieldDefinition(name=field_name, data_type=data_type)


def test_field_rejects_zero_length() -> None:
    with pytest.raises(ValidationError):
        FieldDefinition(name="Material", data_type="string", length=0)


def test_dataset_is_immutable() -> None:
    dataset = DatasetDefinition(name="WaterLine")

    with pytest.raises(ValidationError) as error:
        dataset.name = "SewerLine"

    assert error.value.errors()[0]["type"] == "frozen_instance"


@pytest.mark.parametrize(
    "default",
    [
        object(),
        float("nan"),
        float("inf"),
        float("-inf"),
        {"nested": [float("nan")]},
    ],
    ids=["object", "nan", "positive-infinity", "negative-infinity", "nested-nan"],
)
def test_field_default_rejects_values_outside_finite_json(default: object) -> None:
    with pytest.raises(ValidationError):
        FieldDefinition(name="Material", data_type="string", default=default)


def test_field_default_is_copied_deeply_frozen_and_json_serializable() -> None:
    original = {"options": [{"ratio": 1.25}]}
    field = FieldDefinition(name="Material", data_type="string", default=original)

    original["options"][0]["ratio"] = 9.5
    original["options"].append({"ratio": 2.5})

    assert field.default == {"options": ({"ratio": 1.25},)}
    with pytest.raises(TypeError):
        field.default["options"][0]["ratio"] = 3.5
    with pytest.raises(TypeError):
        field.default["options"][0] = {"ratio": 3.5}
    assert field.model_dump(mode="json")["default"] == {
        "options": [{"ratio": 1.25}]
    }
    assert '"default":{"options":[{"ratio":1.25}]}' in field.model_dump_json()
