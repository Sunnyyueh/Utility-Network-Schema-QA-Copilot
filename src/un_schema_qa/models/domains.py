from pydantic import BaseModel, ConfigDict, Field

from un_schema_qa.models.common import SourceLocation


class DomainCode(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str = Field(min_length=1)
    label: str = Field(min_length=1)
    source_location: SourceLocation | None = None


class DomainDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    codes: tuple[DomainCode, ...] = ()
    source_location: SourceLocation | None = None


class SubtypeDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str = Field(min_length=1)
    label: str = Field(min_length=1)
    source_location: SourceLocation | None = None


class AssetClassification(BaseModel):
    model_config = ConfigDict(frozen=True)

    asset_group: str = Field(min_length=1)
    asset_type: str = Field(min_length=1)
    subtype: str | None = None
    source_location: SourceLocation | None = None
