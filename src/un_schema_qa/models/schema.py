from pydantic import BaseModel, ConfigDict, Field

from un_schema_qa.models.common import SourceLocation
from un_schema_qa.models.json_values import FrozenJsonValue


class FieldDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    data_type: str = Field(min_length=1)
    required: bool = False
    nullable: bool = True
    length: int | None = Field(default=None, ge=1)
    default: FrozenJsonValue = None
    domain: str | None = None
    source_location: SourceLocation | None = None


class DatasetDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    fields: tuple[FieldDefinition, ...] = ()
    source_location: SourceLocation | None = None

    def get_field(self, name: str) -> FieldDefinition | None:
        normalized = name.casefold()
        return next(
            (field for field in self.fields if field.name.casefold() == normalized),
            None,
        )
