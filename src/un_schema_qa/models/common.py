from pydantic import BaseModel, ConfigDict, Field


class SourceLocation(BaseModel):
    model_config = ConfigDict(frozen=True)

    file: str
    sheet: str | None = None
    row: int | None = Field(default=None, ge=1)
    column: str | None = None
