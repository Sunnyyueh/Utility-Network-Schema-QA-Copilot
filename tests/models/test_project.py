import pytest
from pydantic import ValidationError

from un_schema_qa.models.enums import UtilityDomain
from un_schema_qa.models.profiles import UtilityProfile
from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.schema import DatasetDefinition


def _profile() -> UtilityProfile:
    return UtilityProfile(
        name="Water Foundation",
        domain=UtilityDomain.WATER,
        version="1.0.0",
    )


def test_project_resolves_source_and_target_datasets() -> None:
    source = DatasetDefinition(name="LegacyLine")
    target = DatasetDefinition(name="WaterLine")
    project = ValidationProject(
        source_datasets=(source,),
        target_datasets=(target,),
        profile=UtilityProfile(
            name="Water Foundation",
            domain=UtilityDomain.WATER,
            version="1.0.0",
        ),
    )

    assert project.source_dataset("legacyline") == source
    assert project.target_dataset("WATERLINE") == target
    assert project.target_dataset("Missing") is None


def test_validation_project_is_publicly_exported() -> None:
    from un_schema_qa.models import ValidationProject as PublicValidationProject

    assert PublicValidationProject is ValidationProject


def test_project_collection_defaults_are_empty_tuples() -> None:
    project = ValidationProject(profile=_profile())

    assert (
        project.source_datasets,
        project.target_datasets,
        project.mappings,
        project.domains,
        project.subtypes,
        project.assets,
    ) == ((), (), (), (), (), ())


def test_project_serializes_nested_datasets_and_profile_in_json_mode() -> None:
    project = ValidationProject(
        source_datasets=(DatasetDefinition(name="LegacyLine"),),
        target_datasets=(DatasetDefinition(name="WaterLine"),),
        profile=_profile(),
    )

    payload = project.model_dump(mode="json")

    assert payload["source_datasets"] == [
        {"name": "LegacyLine", "fields": [], "source_location": None}
    ]
    assert payload["target_datasets"] == [
        {"name": "WaterLine", "fields": [], "source_location": None}
    ]
    assert payload["profile"]["domain"] == "water"


def test_project_is_immutable() -> None:
    project = ValidationProject(profile=_profile())

    with pytest.raises(ValidationError) as error:
        project.source_datasets = ()

    assert error.value.errors()[0]["type"] == "frozen_instance"
