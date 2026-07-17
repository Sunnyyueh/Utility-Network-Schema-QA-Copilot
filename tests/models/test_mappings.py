import pytest
from pydantic import BaseModel, ValidationError

from un_schema_qa.models.mappings import MappingRule, TransformationDefinition


def test_mapping_rule_preserves_transformation_and_review_metadata() -> None:
    mapping = MappingRule(
        source_dataset="LegacyLine",
        source_field="MAT",
        target_dataset="WaterLine",
        target_field="material",
        transformation=TransformationDefinition(
            expression="value.upper()",
            description="Normalize material codes",
        ),
        reviewer_note="Confirm legacy aliases",
    )

    assert mapping.transformation is not None
    assert mapping.transformation.expression == "value.upper()"
    assert mapping.reviewer_note == "Confirm legacy aliases"


def test_ignored_mapping_can_retain_a_reason() -> None:
    mapping = MappingRule(
        source_dataset="LegacyLine",
        source_field="OLD_ID",
        target_dataset="WaterLine",
        target_field=None,
        ignored=True,
        ignore_reason="Retired identifier",
    )

    assert mapping.ignored is True
    assert mapping.ignore_reason == "Retired identifier"


@pytest.mark.parametrize(
    ("model_type", "values"),
    [
        (TransformationDefinition, {"expression": "", "description": "Normalize values"}),
        (TransformationDefinition, {"expression": "value", "description": ""}),
        (
            MappingRule,
            {
                "source_dataset": "",
                "source_field": "MAT",
                "target_dataset": "WaterLine",
                "target_field": "material",
            },
        ),
        (
            MappingRule,
            {
                "source_dataset": "LegacyLine",
                "source_field": "",
                "target_dataset": "WaterLine",
                "target_field": "material",
            },
        ),
        (
            MappingRule,
            {
                "source_dataset": "LegacyLine",
                "source_field": "MAT",
                "target_dataset": "",
                "target_field": "material",
            },
        ),
    ],
)
def test_mapping_models_reject_empty_required_strings(
    model_type: type[BaseModel], values: dict[str, str]
) -> None:
    with pytest.raises(ValidationError):
        model_type(**values)


def test_mapping_rule_is_immutable() -> None:
    mapping = MappingRule(
        source_dataset="LegacyLine",
        source_field="MAT",
        target_dataset="WaterLine",
        target_field="material",
    )

    with pytest.raises(ValidationError) as error:
        mapping.target_dataset = "SewerLine"

    assert error.value.errors()[0]["type"] == "frozen_instance"
