from pydantic import BaseModel, ConfigDict, Field

from un_schema_qa.models.common import SourceLocation


class TransformationDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    expression: str = Field(min_length=1)
    description: str = Field(min_length=1)


class MappingRule(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_dataset: str = Field(min_length=1)
    source_field: str = Field(min_length=1)
    target_dataset: str = Field(min_length=1)
    target_field: str | None
    transformation: TransformationDefinition | None = None
    ignored: bool = False
    ignore_reason: str | None = None
    reviewer_note: str | None = None
    source_location: SourceLocation | None = None
