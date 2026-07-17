import pytest
from pydantic import BaseModel, ValidationError

from un_schema_qa.models.domains import (
    AssetClassification,
    DomainCode,
    DomainDefinition,
    SubtypeDefinition,
)


def test_domain_and_asset_models_are_json_serializable() -> None:
    domain = DomainDefinition(
        name="MaterialDomain",
        codes=(DomainCode(code="PVC", label="PVC"),),
    )
    subtype = SubtypeDefinition(code="1", label="Main")
    asset = AssetClassification(asset_group="Line", asset_type="Main")

    assert domain.model_dump(mode="json")["codes"][0]["code"] == "PVC"
    assert subtype.model_dump() == {"code": "1", "label": "Main", "source_location": None}
    assert asset.model_dump()["asset_type"] == "Main"


@pytest.mark.parametrize(
    ("model_type", "values"),
    [
        (DomainCode, {"code": "", "label": "PVC"}),
        (DomainCode, {"code": "PVC", "label": ""}),
        (DomainDefinition, {"name": ""}),
        (SubtypeDefinition, {"code": "", "label": "Main"}),
        (SubtypeDefinition, {"code": "1", "label": ""}),
        (AssetClassification, {"asset_group": "", "asset_type": "Main"}),
        (AssetClassification, {"asset_group": "Line", "asset_type": ""}),
    ],
)
def test_domain_and_asset_models_reject_empty_required_strings(
    model_type: type[BaseModel], values: dict[str, str]
) -> None:
    with pytest.raises(ValidationError):
        model_type(**values)


def test_asset_classification_is_immutable() -> None:
    asset = AssetClassification(asset_group="Line", asset_type="Main")

    with pytest.raises(ValidationError) as error:
        asset.asset_type = "Service"

    assert error.value.errors()[0]["type"] == "frozen_instance"
