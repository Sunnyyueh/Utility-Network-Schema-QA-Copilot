from pydantic import BaseModel, ConfigDict

from un_schema_qa.models.domains import (
    AssetClassification,
    DomainDefinition,
    SubtypeDefinition,
)
from un_schema_qa.models.mappings import MappingRule
from un_schema_qa.models.profiles import UtilityProfile
from un_schema_qa.models.schema import DatasetDefinition


class ValidationProject(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_datasets: tuple[DatasetDefinition, ...] = ()
    target_datasets: tuple[DatasetDefinition, ...] = ()
    mappings: tuple[MappingRule, ...] = ()
    domains: tuple[DomainDefinition, ...] = ()
    subtypes: tuple[SubtypeDefinition, ...] = ()
    assets: tuple[AssetClassification, ...] = ()
    profile: UtilityProfile

    def source_dataset(self, name: str) -> DatasetDefinition | None:
        return self._dataset_by_name(self.source_datasets, name)

    def target_dataset(self, name: str) -> DatasetDefinition | None:
        return self._dataset_by_name(self.target_datasets, name)

    @staticmethod
    def _dataset_by_name(
        datasets: tuple[DatasetDefinition, ...],
        name: str,
    ) -> DatasetDefinition | None:
        normalized = name.casefold()
        return next(
            (dataset for dataset in datasets if dataset.name.casefold() == normalized),
            None,
        )
