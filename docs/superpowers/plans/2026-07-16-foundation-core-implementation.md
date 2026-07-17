# Foundation and Deterministic Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Build the installable, typed, offline foundation for Utility Network Schema QA Copilot, including canonical models, four input parsers, parser dispatch, validator contracts, and an error-isolating deterministic engine.

**Architecture:** A Python 3.12 package normalizes CSV, Excel, JSON, and YAML into immutable Pydantic models. Parsers are selected by an explicit registry, while validators implement a small protocol and run through an engine that sorts results, isolates component failures, and never invokes an AI provider.

**Tech Stack:** Python 3.12, uv, Hatchling, Pydantic 2.13.x, Pandas 2.3.x, OpenPyXL 3.1.x, PyYAML 6.x, Pytest, Hypothesis, Ruff, and Mypy.

## Global Constraints

- Python requires version 3.12 or newer and version 3.15 is excluded until all dependencies declare support.
- The deterministic core must run without network access, ArcGIS Pro, ArcPy, or an AI key.
- All Pydantic v2 models set `ConfigDict(frozen=True)` unless a task explicitly defines a mutable builder; ordered collections use tuples.
- Validation reads inputs but never modifies source files or writes to databases.
- Supported input formats are CSV, XLSX, JSON, and YAML.
- Public data structures serialize to stable JSON-compatible values.
- Runtime errors are separate from validation outcomes.
- The project license is Apache License 2.0.
- Dependency resolution is committed in uv.lock.
- Every task follows red-green-refactor and ends with one meaningful conventional commit.
- No task may add an empty commit, whitespace-only commit, fabricated output, or unverified capability claim.

---

## Program Decomposition

The approved v1 specification is intentionally split into independently executable plans.

| Phase | Deliverable | Planned meaningful commits |
| --- | --- | ---: |
| 1 | Foundation, canonical models, parsers, validator protocol, deterministic engine | 18 |
| 2 | Eighteen validation rules and three utility profiles | 24 |
| 3 | JSON, CSV, Markdown, HTML, manifests, and reproducibility | 8 |
| 4 | Hybrid retrieval, citations, model adapters, and explanation agent | 9 |
| 5 | Python API, CLI, MCP server, and Agent Skill | 10 |
| 6 | Streamlit application, security hardening, documentation, CI, and release | 10 |
| **Total** | **Complete v1 program** | **79** |

Each phase receives its own implementation plan before execution. This plan covers Phase 1 only and leaves the repository with a working, tested offline library foundation.

## Phase 1 File Map

~~~text
.
├── .gitignore
├── pyproject.toml
├── uv.lock
├── src/
│   └── un_schema_qa/
│       ├── __init__.py
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── protocols.py
│       │   ├── registry.py
│       │   └── runner.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── common.py
│       │   ├── domains.py
│       │   ├── enums.py
│       │   ├── mappings.py
│       │   ├── profiles.py
│       │   ├── project.py
│       │   ├── results.py
│       │   └── schema.py
│       └── parsers/
│           ├── __init__.py
│           ├── base.py
│           ├── csv_parser.py
│           ├── excel_parser.py
│           ├── json_parser.py
│           ├── registry.py
│           └── yaml_parser.py
└── tests/
    ├── engine/
    ├── models/
    ├── parsers/
    └── test_package.py
~~~

## Task 1: Package Foundation

**Files:**

- Create: pyproject.toml
- Create: .gitignore
- Create: tests/test_package.py
- Create: src/un_schema_qa/__init__.py
- Create: uv.lock through uv lock

**Interfaces:**

- Consumes: No project interfaces.
- Produces: un_schema_qa.__version__ as a string equal to 0.1.0.

- [ ] **Step 1: Create dependency metadata and the failing import test**

~~~toml
[build-system]
requires = ["hatchling>=1.27,<2"]
build-backend = "hatchling.build"

[project]
name = "utility-network-schema-qa"
version = "0.1.0"
description = "Deterministic and AI-assisted Utility Network schema validation"
readme = "README.md"
requires-python = ">=3.12,<3.15"
license = "Apache-2.0"
authors = [{ name = "Sunnyyueh" }]
dependencies = [
  "openpyxl>=3.1,<4",
  "pandas>=2.3,<3",
  "pydantic>=2.13,<3",
  "pyyaml>=6,<7",
]

[dependency-groups]
dev = [
  "hypothesis>=6.140,<7",
  "mypy>=1.17,<2",
  "pandas-stubs>=2.3,<3",
  "pytest>=8.4,<9",
  "pytest-cov>=6.2,<7",
  "ruff>=0.12,<1",
  "types-pyyaml>=6.0,<7",
]

[tool.hatch.build.targets.wheel]
packages = ["src/un_schema_qa"]

[tool.pytest.ini_options]
addopts = "-ra --strict-config --strict-markers"
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "RUF"]

[tool.mypy]
python_version = "3.12"
strict = true
packages = ["un_schema_qa"]
~~~

~~~gitignore
.DS_Store
.coverage
.mypy_cache/
.pytest_cache/
.ruff_cache/
.venv/
.superpowers/
.worktrees/
__pycache__/
build/
dist/
htmlcov/
*.egg-info/
~~~

~~~python
# tests/test_package.py
from un_schema_qa import __version__


def test_package_exposes_version() -> None:
    assert __version__ == "0.1.0"
~~~

~~~python
# src/un_schema_qa/__init__.py
"""Utility Network Schema QA Copilot."""
~~~

- [ ] **Step 2: Resolve dependencies and verify the test fails**

Run: uv lock && uv sync --all-groups && uv run pytest tests/test_package.py -v

Expected: FAIL during collection with ImportError because __version__ is not defined.

- [ ] **Step 3: Add the minimal package module**

~~~python
# src/un_schema_qa/__init__.py
"""Utility Network Schema QA Copilot."""

__version__ = "0.1.0"
~~~

- [ ] **Step 4: Verify package, lint, and type checking**

Run: uv run pytest tests/test_package.py -v && uv run ruff check . && uv run mypy

Expected: 1 passed, Ruff exits 0, and Mypy exits 0.

- [ ] **Step 5: Commit**

~~~bash
git add .gitignore pyproject.toml uv.lock src/un_schema_qa/__init__.py tests/test_package.py
git commit -m "build: initialize Python package"
~~~

## Task 2: Shared Enumerations

**Files:**

- Create: src/un_schema_qa/models/__init__.py
- Create: src/un_schema_qa/models/enums.py
- Create: tests/models/test_enums.py

**Interfaces:**

- Consumes: Pydantic-compatible string enum semantics.
- Produces: CheckStatus, RunStatus, UtilityDomain, and InputFormat.

- [ ] **Step 1: Write the failing enum test**

~~~python
# tests/models/test_enums.py
from un_schema_qa.models.enums import CheckStatus, InputFormat, RunStatus, UtilityDomain


def test_public_enums_use_stable_string_values() -> None:
    assert [item.value for item in CheckStatus] == ["pass", "warning", "fail", "blocker"]
    assert [item.value for item in RunStatus] == [
        "completed",
        "completed_with_errors",
        "failed",
    ]
    assert [item.value for item in UtilityDomain] == ["water", "wastewater", "stormwater"]
    assert [item.value for item in InputFormat] == ["csv", "xlsx", "json", "yaml"]
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/models/test_enums.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.models.enums.

- [ ] **Step 3: Implement the enums**

~~~python
# src/un_schema_qa/models/enums.py
from enum import Enum


class CheckStatus(str, Enum):
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    BLOCKER = "blocker"


class RunStatus(str, Enum):
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"


class UtilityDomain(str, Enum):
    WATER = "water"
    WASTEWATER = "wastewater"
    STORMWATER = "stormwater"


class InputFormat(str, Enum):
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"
    YAML = "yaml"
~~~

~~~python
# src/un_schema_qa/models/__init__.py
"""Canonical public models."""
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/models/test_enums.py -v && uv run ruff check . && uv run mypy

Expected: 1 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/models tests/models/test_enums.py
git commit -m "feat: add shared model enums"
~~~

## Task 3: Source Location Model

**Files:**

- Create: src/un_schema_qa/models/common.py
- Create: tests/models/test_common.py

**Interfaces:**

- Consumes: Pydantic BaseModel.
- Produces: SourceLocation(file, sheet, row, column) with immutable validated coordinates.

- [ ] **Step 1: Write the failing model tests**

~~~python
# tests/models/test_common.py
import pytest
from pydantic import ValidationError

from un_schema_qa.models.common import SourceLocation


def test_source_location_serializes_only_supplied_coordinates() -> None:
    location = SourceLocation(file="schema.xlsx", sheet="Fields", row=4, column="name")
    assert location.model_dump(exclude_none=True) == {
        "file": "schema.xlsx",
        "sheet": "Fields",
        "row": 4,
        "column": "name",
    }


def test_source_location_rejects_zero_based_rows() -> None:
    with pytest.raises(ValidationError):
        SourceLocation(file="schema.csv", row=0)
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/models/test_common.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.models.common.

- [ ] **Step 3: Implement SourceLocation**

~~~python
# src/un_schema_qa/models/common.py
from pydantic import BaseModel, ConfigDict, Field


class SourceLocation(BaseModel):
    model_config = ConfigDict(frozen=True)

    file: str
    sheet: str | None = None
    row: int | None = Field(default=None, ge=1)
    column: str | None = None
~~~

- [ ] **Step 4: Run focused and full model tests**

Run: uv run pytest tests/models -v && uv run ruff check . && uv run mypy

Expected: All model tests pass and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/models/common.py tests/models/test_common.py
git commit -m "feat: add immutable source locations"
~~~

## Task 4: Dataset and Field Models

**Files:**

- Create: src/un_schema_qa/models/schema.py
- Create: tests/models/test_schema.py

**Interfaces:**

- Consumes: SourceLocation.
- Produces: FieldDefinition and DatasetDefinition.get_field(name).

- [ ] **Step 1: Write failing schema model tests**

~~~python
# tests/models/test_schema.py
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
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/models/test_schema.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.models.schema.

- [ ] **Step 3: Implement schema models**

~~~python
# src/un_schema_qa/models/schema.py
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from un_schema_qa.models.common import SourceLocation


class FieldDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    data_type: str = Field(min_length=1)
    required: bool = False
    nullable: bool = True
    length: int | None = Field(default=None, ge=1)
    default: Any = None
    domain: str | None = None
    source_location: SourceLocation | None = None


class DatasetDefinition(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    fields: tuple[FieldDefinition, ...] = ()
    source_location: SourceLocation | None = None

    def get_field(self, name: str) -> FieldDefinition | None:
        normalized = name.casefold()
        return next((field for field in self.fields if field.name.casefold() == normalized), None)
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/models/test_schema.py -v && uv run ruff check . && uv run mypy

Expected: 2 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/models/schema.py tests/models/test_schema.py
git commit -m "feat: add dataset and field models"
~~~

## Task 5: Domain and Asset Models

**Files:**

- Create: src/un_schema_qa/models/domains.py
- Create: tests/models/test_domains.py

**Interfaces:**

- Consumes: SourceLocation.
- Produces: DomainCode, DomainDefinition, SubtypeDefinition, and AssetClassification.

- [ ] **Step 1: Write the failing domain test**

~~~python
# tests/models/test_domains.py
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
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/models/test_domains.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.models.domains.

- [ ] **Step 3: Implement domain models**

~~~python
# src/un_schema_qa/models/domains.py
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
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/models/test_domains.py -v && uv run ruff check . && uv run mypy

Expected: 1 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/models/domains.py tests/models/test_domains.py
git commit -m "feat: add domain and asset models"
~~~

## Task 6: Mapping Models

**Files:**

- Create: src/un_schema_qa/models/mappings.py
- Create: tests/models/test_mappings.py

**Interfaces:**

- Consumes: SourceLocation.
- Produces: TransformationDefinition and MappingRule.

- [ ] **Step 1: Write the failing mapping tests**

~~~python
# tests/models/test_mappings.py
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
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/models/test_mappings.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.models.mappings.

- [ ] **Step 3: Implement mapping models**

~~~python
# src/un_schema_qa/models/mappings.py
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
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/models/test_mappings.py -v && uv run ruff check . && uv run mypy

Expected: 2 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/models/mappings.py tests/models/test_mappings.py
git commit -m "feat: add source target mapping models"
~~~

## Task 7: Utility Profile Models

**Files:**

- Create: src/un_schema_qa/models/profiles.py
- Create: tests/models/test_profiles.py

**Interfaces:**

- Consumes: UtilityDomain.
- Produces: RuleConfiguration and UtilityProfile with validated finding-code keys.

- [ ] **Step 1: Write failing profile contract tests**

~~~python
# tests/models/test_profiles.py
import pytest
from pydantic import ValidationError

from un_schema_qa.models.enums import CheckStatus, UtilityDomain
from un_schema_qa.models.profiles import RuleConfiguration, UtilityProfile


def test_profile_accepts_versioned_rule_configuration() -> None:
    profile = UtilityProfile(
        name="Water Foundation",
        domain=UtilityDomain.WATER,
        version="1.0.0",
        rule_configuration=RuleConfiguration(
            enabled_codes=("UNQA-V001", "UNQA-V017"),
            severity_overrides={"UNQA-V017": CheckStatus.WARNING},
        ),
    )
    assert profile.rule_configuration.enabled_codes == ("UNQA-V001", "UNQA-V017")


def test_profile_rejects_invalid_rule_codes() -> None:
    with pytest.raises(ValidationError):
        RuleConfiguration(enabled_codes=("INVALID",))
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/models/test_profiles.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.models.profiles.

- [ ] **Step 3: Implement profile models**

~~~python
# src/un_schema_qa/models/profiles.py
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from un_schema_qa.models.enums import CheckStatus, UtilityDomain

RULE_CODE_PATTERN = re.compile(r"^UNQA-V\d{3}$")


class RuleConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    enabled_codes: tuple[str, ...] = ()
    severity_overrides: dict[str, CheckStatus] = Field(default_factory=dict)

    @field_validator("enabled_codes")
    @classmethod
    def validate_enabled_codes(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if any(RULE_CODE_PATTERN.fullmatch(value) is None for value in values):
            raise ValueError("enabled_codes must use UNQA-V### format")
        return values

    @field_validator("severity_overrides")
    @classmethod
    def validate_override_codes(
        cls,
        values: dict[str, CheckStatus],
    ) -> dict[str, CheckStatus]:
        if any(RULE_CODE_PATTERN.fullmatch(value) is None for value in values):
            raise ValueError("severity_overrides keys must use UNQA-V### format")
        return values


class UtilityProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    domain: UtilityDomain
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    terminology: dict[str, str] = Field(default_factory=dict)
    expected_asset_categories: tuple[str, ...] = ()
    classification_constraints: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    rule_configuration: RuleConfiguration = Field(default_factory=RuleConfiguration)
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/models/test_profiles.py -v && uv run ruff check . && uv run mypy

Expected: 2 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/models/profiles.py tests/models/test_profiles.py
git commit -m "feat: add utility profile contracts"
~~~

## Task 8: Validation Result Models

**Files:**

- Create: src/un_schema_qa/models/results.py
- Create: tests/models/test_results.py

**Interfaces:**

- Consumes: CheckStatus, RunStatus, UtilityDomain, and SourceLocation.
- Produces: CheckResult, RunError, RunMetadata, and ValidationRun.

- [ ] **Step 1: Write failing result model tests**

~~~python
# tests/models/test_results.py
from datetime import UTC, datetime

from un_schema_qa.models.enums import CheckStatus, RunStatus, UtilityDomain
from un_schema_qa.models.results import CheckResult, RunMetadata, ValidationRun


def test_validation_run_serializes_a_complete_result() -> None:
    result = CheckResult(
        finding_code="UNQA-V001",
        rule_version="1.0.0",
        status=CheckStatus.PASS,
        severity_rank=0,
        profile=UtilityDomain.WATER,
        expected={"required": ["name"]},
        actual={"present": ["name"]},
        evidence={"columns": ["name"]},
        remediation_category="none",
        remediation_guidance="No action required.",
    )
    run = ValidationRun(
        metadata=RunMetadata(
            run_id="run-001",
            started_at=datetime(2026, 7, 16, tzinfo=UTC),
            ruleset_version="1.0.0",
            profile_version="1.0.0",
        ),
        status=RunStatus.COMPLETED,
        results=(result,),
    )
    payload = run.model_dump(mode="json")
    assert payload["results"][0]["finding_code"] == "UNQA-V001"
    assert payload["status"] == "completed"
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/models/test_results.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.models.results.

- [ ] **Step 3: Implement result models**

~~~python
# src/un_schema_qa/models/results.py
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from un_schema_qa.models.common import SourceLocation
from un_schema_qa.models.enums import CheckStatus, RunStatus, UtilityDomain


class CheckResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    finding_code: str = Field(pattern=r"^UNQA-V\d{3}$")
    rule_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    status: CheckStatus
    severity_rank: int = Field(ge=0, le=100)
    profile: UtilityDomain
    dataset: str | None = None
    field: str | None = None
    domain: str | None = None
    source_location: SourceLocation | None = None
    expected: Any
    actual: Any
    evidence: dict[str, Any]
    remediation_category: str = Field(min_length=1)
    remediation_guidance: str = Field(min_length=1)


class RunError(BaseModel):
    model_config = ConfigDict(frozen=True)

    category: str = Field(min_length=1)
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    component: str = Field(min_length=1)
    recoverable: bool
    source_location: SourceLocation | None = None


class RunMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str = Field(min_length=1)
    started_at: datetime
    ruleset_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    profile_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")


class ValidationRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    metadata: RunMetadata
    status: RunStatus
    results: tuple[CheckResult, ...] = ()
    errors: tuple[RunError, ...] = ()
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/models/test_results.py -v && uv run ruff check . && uv run mypy

Expected: 1 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/models/results.py tests/models/test_results.py
git commit -m "feat: add validation result contracts"
~~~

## Task 9: Validation Project Aggregate

**Files:**

- Create: src/un_schema_qa/models/project.py
- Modify: src/un_schema_qa/models/__init__.py
- Create: tests/models/test_project.py

**Interfaces:**

- Consumes: DatasetDefinition, DomainDefinition, SubtypeDefinition, AssetClassification, MappingRule, and UtilityProfile.
- Produces: ValidationProject with case-insensitive source_dataset and target_dataset lookup.

- [ ] **Step 1: Write failing project aggregate tests**

~~~python
# tests/models/test_project.py
from un_schema_qa.models.enums import UtilityDomain
from un_schema_qa.models.profiles import UtilityProfile
from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.schema import DatasetDefinition


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
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/models/test_project.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.models.project.

- [ ] **Step 3: Implement the aggregate and public exports**

~~~python
# src/un_schema_qa/models/project.py
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
~~~

~~~python
# src/un_schema_qa/models/__init__.py
"""Canonical public models."""

from un_schema_qa.models.project import ValidationProject

__all__ = ["ValidationProject"]
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/models/test_project.py -v && uv run ruff check . && uv run mypy

Expected: 1 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/models tests/models/test_project.py
git commit -m "feat: add validation project aggregate"
~~~

## Task 10: Parser Contracts and Structured Data Normalization

**Files:**

- Create: src/un_schema_qa/parsers/__init__.py
- Create: src/un_schema_qa/parsers/base.py
- Create: tests/parsers/test_base.py

**Interfaces:**

- Consumes: InputFormat.
- Produces: InputParseError, ParsedSheet, ParsedDocument, Parser, and document_from_structured_data.

- [ ] **Step 1: Write failing parser contract tests**

~~~python
# tests/parsers/test_base.py
from pathlib import Path

import pytest

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import (
    InputParseError,
    document_from_structured_data,
)


def test_structured_list_becomes_a_default_sheet() -> None:
    document = document_from_structured_data(
        path=Path("schema.json"),
        input_format=InputFormat.JSON,
        data=[{"name": "Material"}],
    )
    assert document.sheets[0].name == "data"
    assert document.sheets[0].rows == ({"name": "Material"},)


def test_structured_mapping_becomes_named_sheets() -> None:
    document = document_from_structured_data(
        path=Path("schema.yaml"),
        input_format=InputFormat.YAML,
        data={"fields": [{"name": "Material"}], "domains": []},
    )
    assert [sheet.name for sheet in document.sheets] == ["domains", "fields"]


def test_structured_scalar_is_rejected() -> None:
    with pytest.raises(InputParseError, match="STRUCTURE_INVALID"):
        document_from_structured_data(
            path=Path("schema.json"),
            input_format=InputFormat.JSON,
            data="not-a-table",
        )
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/parsers/test_base.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.parsers.base.

- [ ] **Step 3: Implement parser contracts and structured normalization**

~~~python
# src/un_schema_qa/parsers/base.py
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from un_schema_qa.models.enums import InputFormat


class InputParseError(Exception):
    def __init__(self, code: str, path: Path, detail: str) -> None:
        self.code = code
        self.path = path
        self.detail = detail
        super().__init__(f"{code}: {path}: {detail}")


class ParsedSheet(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    rows: tuple[dict[str, Any], ...] = ()


class ParsedDocument(BaseModel):
    model_config = ConfigDict(frozen=True)

    path: str
    input_format: InputFormat
    sheets: tuple[ParsedSheet, ...]


class Parser(Protocol):
    def parse(self, path: Path) -> ParsedDocument:
        """Parse one supported input document."""
        ...


def document_from_structured_data(
    path: Path,
    input_format: InputFormat,
    data: Any,
) -> ParsedDocument:
    if isinstance(data, list):
        sheets = (ParsedSheet(name="data", rows=_validate_rows(path, "data", data)),)
    elif isinstance(data, dict):
        sheets = tuple(
            ParsedSheet(name=name, rows=_validate_rows(path, name, rows))
            for name, rows in sorted(data.items())
        )
    else:
        raise InputParseError("STRUCTURE_INVALID", path, "expected a list or sheet mapping")
    return ParsedDocument(path=str(path), input_format=input_format, sheets=sheets)


def _validate_rows(
    path: Path,
    sheet: str,
    rows: Any,
) -> tuple[dict[str, Any], ...]:
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise InputParseError(
            "ROWS_INVALID",
            path,
            f"sheet {sheet!r} must contain a list of objects",
        )
    return tuple(rows)
~~~

~~~python
# src/un_schema_qa/parsers/__init__.py
"""Input parser adapters."""
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/parsers/test_base.py -v && uv run ruff check . && uv run mypy

Expected: 3 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/parsers tests/parsers/test_base.py
git commit -m "feat: define parser contracts"
~~~

## Task 11: CSV Parser

**Files:**

- Create: src/un_schema_qa/parsers/csv_parser.py
- Create: tests/parsers/test_csv_parser.py

**Interfaces:**

- Consumes: ParsedDocument, ParsedSheet, and InputParseError.
- Produces: CsvParser.parse(path) returning one sheet named data.

- [ ] **Step 1: Write failing CSV parser tests**

~~~python
# tests/parsers/test_csv_parser.py
from pathlib import Path

import pytest

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import InputParseError
from un_schema_qa.parsers.csv_parser import CsvParser


def test_csv_parser_returns_records(tmp_path: Path) -> None:
    path = tmp_path / "schema.csv"
    path.write_text("name,data_type\nMaterial,string\n", encoding="utf-8")

    document = CsvParser().parse(path)

    assert document.input_format is InputFormat.CSV
    assert document.sheets[0].rows == ({"name": "Material", "data_type": "string"},)


def test_csv_parser_wraps_decode_errors(tmp_path: Path) -> None:
    path = tmp_path / "schema.csv"
    path.write_bytes(b"\xff\xfe")

    with pytest.raises(InputParseError, match="CSV_PARSE_FAILED"):
        CsvParser().parse(path)
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/parsers/test_csv_parser.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.parsers.csv_parser.

- [ ] **Step 3: Implement CsvParser**

~~~python
# src/un_schema_qa/parsers/csv_parser.py
from pathlib import Path

import pandas as pd

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import InputParseError, ParsedDocument, ParsedSheet


class CsvParser:
    def parse(self, path: Path) -> ParsedDocument:
        try:
            frame = pd.read_csv(path, dtype=object, encoding="utf-8")
        except (OSError, UnicodeError, pd.errors.ParserError) as exc:
            raise InputParseError("CSV_PARSE_FAILED", path, str(exc)) from exc
        normalized = frame.astype(object).where(pd.notna(frame), None)
        rows = tuple(
            {str(key): value for key, value in record.items()}
            for record in normalized.to_dict(orient="records")
        )
        return ParsedDocument(
            path=str(path),
            input_format=InputFormat.CSV,
            sheets=(ParsedSheet(name="data", rows=rows),),
        )
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/parsers/test_csv_parser.py -v && uv run ruff check . && uv run mypy

Expected: 2 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/parsers/csv_parser.py tests/parsers/test_csv_parser.py
git commit -m "feat: parse CSV inputs"
~~~

## Task 12: JSON Parser

**Files:**

- Create: src/un_schema_qa/parsers/json_parser.py
- Create: tests/parsers/test_json_parser.py

**Interfaces:**

- Consumes: document_from_structured_data.
- Produces: JsonParser.parse(path).

- [ ] **Step 1: Write failing JSON parser tests**

~~~python
# tests/parsers/test_json_parser.py
from pathlib import Path

import pytest

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import InputParseError
from un_schema_qa.parsers.json_parser import JsonParser


def test_json_parser_reads_named_sheets(tmp_path: Path) -> None:
    path = tmp_path / "schema.json"
    path.write_text('{"fields": [{"name": "Material"}]}', encoding="utf-8")

    document = JsonParser().parse(path)

    assert document.input_format is InputFormat.JSON
    assert document.sheets[0].name == "fields"


def test_json_parser_wraps_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "schema.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(InputParseError, match="JSON_PARSE_FAILED"):
        JsonParser().parse(path)
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/parsers/test_json_parser.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.parsers.json_parser.

- [ ] **Step 3: Implement JsonParser**

~~~python
# src/un_schema_qa/parsers/json_parser.py
import json
from pathlib import Path

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import (
    InputParseError,
    ParsedDocument,
    document_from_structured_data,
)


class JsonParser:
    def parse(self, path: Path) -> ParsedDocument:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise InputParseError("JSON_PARSE_FAILED", path, str(exc)) from exc
        return document_from_structured_data(path, InputFormat.JSON, data)
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/parsers/test_json_parser.py -v && uv run ruff check . && uv run mypy

Expected: 2 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/parsers/json_parser.py tests/parsers/test_json_parser.py
git commit -m "feat: parse JSON inputs"
~~~

## Task 13: YAML Parser

**Files:**

- Create: src/un_schema_qa/parsers/yaml_parser.py
- Create: tests/parsers/test_yaml_parser.py

**Interfaces:**

- Consumes: document_from_structured_data.
- Produces: YamlParser.parse(path) using safe YAML loading.

- [ ] **Step 1: Write failing YAML parser tests**

~~~python
# tests/parsers/test_yaml_parser.py
from pathlib import Path

import pytest

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import InputParseError
from un_schema_qa.parsers.yaml_parser import YamlParser


def test_yaml_parser_reads_named_sheets(tmp_path: Path) -> None:
    path = tmp_path / "schema.yaml"
    path.write_text("fields:\n  - name: Material\n", encoding="utf-8")

    document = YamlParser().parse(path)

    assert document.input_format is InputFormat.YAML
    assert document.sheets[0].rows[0]["name"] == "Material"


def test_yaml_parser_wraps_invalid_yaml(tmp_path: Path) -> None:
    path = tmp_path / "schema.yaml"
    path.write_text("fields: [", encoding="utf-8")

    with pytest.raises(InputParseError, match="YAML_PARSE_FAILED"):
        YamlParser().parse(path)
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/parsers/test_yaml_parser.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.parsers.yaml_parser.

- [ ] **Step 3: Implement YamlParser**

~~~python
# src/un_schema_qa/parsers/yaml_parser.py
from pathlib import Path

import yaml

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import (
    InputParseError,
    ParsedDocument,
    document_from_structured_data,
)


class YamlParser:
    def parse(self, path: Path) -> ParsedDocument:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise InputParseError("YAML_PARSE_FAILED", path, str(exc)) from exc
        return document_from_structured_data(path, InputFormat.YAML, data)
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/parsers/test_yaml_parser.py -v && uv run ruff check . && uv run mypy

Expected: 2 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/parsers/yaml_parser.py tests/parsers/test_yaml_parser.py
git commit -m "feat: parse YAML inputs safely"
~~~

## Task 14: Excel Parser

**Files:**

- Create: src/un_schema_qa/parsers/excel_parser.py
- Create: tests/parsers/test_excel_parser.py

**Interfaces:**

- Consumes: ParsedDocument, ParsedSheet, and InputParseError.
- Produces: ExcelParser.parse(path) preserving sorted sheet names and normalized nulls.

- [ ] **Step 1: Write failing Excel parser tests**

~~~python
# tests/parsers/test_excel_parser.py
from pathlib import Path

import pandas as pd

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.excel_parser import ExcelParser


def test_excel_parser_reads_all_sheets_in_stable_order(tmp_path: Path) -> None:
    path = tmp_path / "schema.xlsx"
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame([{"name": "PVC"}]).to_excel(
            writer,
            sheet_name="Domains",
            index=False,
        )
        pd.DataFrame([{"name": "Material", "length": None}]).to_excel(
            writer,
            sheet_name="Fields",
            index=False,
        )

    document = ExcelParser().parse(path)

    assert document.input_format is InputFormat.XLSX
    assert [sheet.name for sheet in document.sheets] == ["Domains", "Fields"]
    assert document.sheets[1].rows[0]["length"] is None
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/parsers/test_excel_parser.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.parsers.excel_parser.

- [ ] **Step 3: Implement ExcelParser**

~~~python
# src/un_schema_qa/parsers/excel_parser.py
from pathlib import Path

import pandas as pd

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import InputParseError, ParsedDocument, ParsedSheet


class ExcelParser:
    def parse(self, path: Path) -> ParsedDocument:
        try:
            workbook = pd.read_excel(path, sheet_name=None, dtype=object)
        except (OSError, ValueError) as exc:
            raise InputParseError("XLSX_PARSE_FAILED", path, str(exc)) from exc
        sheets = tuple(
            ParsedSheet(
                name=name,
                rows=tuple(
                    {str(key): value for key, value in record.items()}
                    for record in frame.astype(object)
                    .where(pd.notna(frame), None)
                    .to_dict(orient="records")
                ),
            )
            for name, frame in sorted(workbook.items())
        )
        return ParsedDocument(
            path=str(path),
            input_format=InputFormat.XLSX,
            sheets=sheets,
        )
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/parsers/test_excel_parser.py -v && uv run ruff check . && uv run mypy

Expected: 1 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/parsers/excel_parser.py tests/parsers/test_excel_parser.py
git commit -m "feat: parse Excel workbooks"
~~~

## Task 15: Parser Registry and Dispatch

**Files:**

- Create: src/un_schema_qa/parsers/registry.py
- Modify: src/un_schema_qa/parsers/__init__.py
- Create: tests/parsers/test_registry.py

**Interfaces:**

- Consumes: CsvParser, ExcelParser, JsonParser, YamlParser, and InputParseError.
- Produces: ParserRegistry and parse_document(path).

- [ ] **Step 1: Write failing registry tests**

~~~python
# tests/parsers/test_registry.py
from pathlib import Path

import pytest

from un_schema_qa.models.enums import InputFormat
from un_schema_qa.parsers.base import InputParseError
from un_schema_qa.parsers.registry import parse_document


def test_parse_document_dispatches_by_suffix(tmp_path: Path) -> None:
    path = tmp_path / "schema.json"
    path.write_text('[{"name": "Material"}]', encoding="utf-8")

    assert parse_document(path).input_format is InputFormat.JSON


def test_parse_document_rejects_unknown_suffix(tmp_path: Path) -> None:
    path = tmp_path / "schema.txt"
    path.write_text("name", encoding="utf-8")

    with pytest.raises(InputParseError, match="FORMAT_UNSUPPORTED"):
        parse_document(path)
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/parsers/test_registry.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.parsers.registry.

- [ ] **Step 3: Implement parser dispatch**

~~~python
# src/un_schema_qa/parsers/registry.py
from pathlib import Path

from un_schema_qa.parsers.base import InputParseError, ParsedDocument, Parser
from un_schema_qa.parsers.csv_parser import CsvParser
from un_schema_qa.parsers.excel_parser import ExcelParser
from un_schema_qa.parsers.json_parser import JsonParser
from un_schema_qa.parsers.yaml_parser import YamlParser


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: dict[str, Parser] = {}

    def register(self, suffix: str, parser: Parser) -> None:
        self._parsers[suffix.casefold()] = parser

    def parse(self, path: Path) -> ParsedDocument:
        parser = self._parsers.get(path.suffix.casefold())
        if parser is None:
            raise InputParseError(
                "FORMAT_UNSUPPORTED",
                path,
                f"unsupported suffix {path.suffix!r}",
            )
        return parser.parse(path)


DEFAULT_REGISTRY = ParserRegistry()
DEFAULT_REGISTRY.register(".csv", CsvParser())
DEFAULT_REGISTRY.register(".xlsx", ExcelParser())
DEFAULT_REGISTRY.register(".json", JsonParser())
DEFAULT_REGISTRY.register(".yaml", YamlParser())
DEFAULT_REGISTRY.register(".yml", YamlParser())


def parse_document(path: Path) -> ParsedDocument:
    return DEFAULT_REGISTRY.parse(path)
~~~

~~~python
# src/un_schema_qa/parsers/__init__.py
"""Input parser adapters."""

from un_schema_qa.parsers.registry import parse_document

__all__ = ["parse_document"]
~~~

- [ ] **Step 4: Run all parser and quality checks**

Run: uv run pytest tests/parsers -v && uv run ruff check . && uv run mypy

Expected: All parser tests pass and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/parsers tests/parsers/test_registry.py
git commit -m "feat: dispatch supported input parsers"
~~~

## Task 16: Validator Protocol

**Files:**

- Create: src/un_schema_qa/engine/__init__.py
- Create: src/un_schema_qa/engine/protocols.py
- Create: tests/engine/test_protocols.py

**Interfaces:**

- Consumes: ValidationProject and CheckResult.
- Produces: runtime-checkable Validator protocol with code, rule_version, and validate(project).

- [ ] **Step 1: Write the failing protocol test**

~~~python
# tests/engine/test_protocols.py
from un_schema_qa.engine.protocols import Validator
from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.results import CheckResult


class ExampleValidator:
    code = "UNQA-V001"
    rule_version = "1.0.0"

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        return ()


def test_validator_protocol_accepts_matching_implementation() -> None:
    assert isinstance(ExampleValidator(), Validator)
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/engine/test_protocols.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.engine.protocols.

- [ ] **Step 3: Implement the protocol**

~~~python
# src/un_schema_qa/engine/protocols.py
from typing import Protocol, runtime_checkable

from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.results import CheckResult


@runtime_checkable
class Validator(Protocol):
    code: str
    rule_version: str

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        """Return deterministic check results for one rule."""
        ...
~~~

~~~python
# src/un_schema_qa/engine/__init__.py
"""Deterministic validation engine."""
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/engine/test_protocols.py -v && uv run ruff check . && uv run mypy

Expected: 1 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/engine tests/engine/test_protocols.py
git commit -m "feat: define validator protocol"
~~~

## Task 17: Validator Registry

**Files:**

- Create: src/un_schema_qa/engine/registry.py
- Create: tests/engine/test_registry.py

**Interfaces:**

- Consumes: Validator.
- Produces: ValidatorRegistry.register, ValidatorRegistry.get, and ValidatorRegistry.ordered.

- [ ] **Step 1: Write failing registry tests**

~~~python
# tests/engine/test_registry.py
import pytest

from un_schema_qa.engine.registry import ValidatorRegistry
from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.results import CheckResult


class StubValidator:
    def __init__(self, code: str) -> None:
        self.code = code
        self.rule_version = "1.0.0"

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        return ()


def test_registry_returns_validators_in_code_order() -> None:
    registry = ValidatorRegistry()
    registry.register(StubValidator("UNQA-V002"))
    registry.register(StubValidator("UNQA-V001"))
    assert [validator.code for validator in registry.ordered()] == [
        "UNQA-V001",
        "UNQA-V002",
    ]


def test_registry_rejects_duplicate_codes() -> None:
    registry = ValidatorRegistry()
    registry.register(StubValidator("UNQA-V001"))
    with pytest.raises(ValueError, match="already registered"):
        registry.register(StubValidator("UNQA-V001"))
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/engine/test_registry.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.engine.registry.

- [ ] **Step 3: Implement ValidatorRegistry**

~~~python
# src/un_schema_qa/engine/registry.py
import re

from un_schema_qa.engine.protocols import Validator

RULE_CODE_PATTERN = re.compile(r"^UNQA-V\d{3}$")


class ValidatorRegistry:
    def __init__(self) -> None:
        self._validators: dict[str, Validator] = {}

    def register(self, validator: Validator) -> None:
        if RULE_CODE_PATTERN.fullmatch(validator.code) is None:
            raise ValueError(f"invalid validator code {validator.code!r}")
        if validator.code in self._validators:
            raise ValueError(f"validator {validator.code!r} is already registered")
        self._validators[validator.code] = validator

    def get(self, code: str) -> Validator | None:
        return self._validators.get(code)

    def ordered(self) -> tuple[Validator, ...]:
        return tuple(self._validators[code] for code in sorted(self._validators))
~~~

- [ ] **Step 4: Run focused and quality checks**

Run: uv run pytest tests/engine/test_registry.py -v && uv run ruff check . && uv run mypy

Expected: 2 passed and both quality commands exit 0.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/engine/registry.py tests/engine/test_registry.py
git commit -m "feat: register validators deterministically"
~~~

## Task 18: Error-Isolating Deterministic Runner

**Files:**

- Create: src/un_schema_qa/engine/runner.py
- Modify: src/un_schema_qa/engine/__init__.py
- Create: tests/engine/test_runner.py

**Interfaces:**

- Consumes: ValidatorRegistry, ValidationProject, CheckResult, RunError, RunMetadata, and ValidationRun.
- Produces: ValidationEngine.run(project, run_id, ruleset_version).

- [ ] **Step 1: Write failing engine behavior tests**

~~~python
# tests/engine/test_runner.py
from datetime import UTC, datetime

from un_schema_qa.engine.registry import ValidatorRegistry
from un_schema_qa.engine.runner import ValidationEngine
from un_schema_qa.models.enums import CheckStatus, RunStatus, UtilityDomain
from un_schema_qa.models.profiles import UtilityProfile
from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.results import CheckResult


class PassingValidator:
    code = "UNQA-V001"
    rule_version = "1.0.0"

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        return (
            CheckResult(
                finding_code=self.code,
                rule_version=self.rule_version,
                status=CheckStatus.PASS,
                severity_rank=0,
                profile=project.profile.domain,
                expected={"required": ["name"]},
                actual={"present": ["name"]},
                evidence={"columns": ["name"]},
                remediation_category="none",
                remediation_guidance="No action required.",
            ),
        )


class FailingValidator:
    code = "UNQA-V002"
    rule_version = "1.0.0"

    def validate(self, project: ValidationProject) -> tuple[CheckResult, ...]:
        raise RuntimeError("validator crashed")


def test_engine_preserves_results_when_one_validator_fails() -> None:
    registry = ValidatorRegistry()
    registry.register(FailingValidator())
    registry.register(PassingValidator())
    engine = ValidationEngine(
        registry,
        clock=lambda: datetime(2026, 7, 16, tzinfo=UTC),
    )
    project = ValidationProject(
        profile=UtilityProfile(
            name="Water Foundation",
            domain=UtilityDomain.WATER,
            version="1.0.0",
        ),
    )

    run = engine.run(project, run_id="run-001", ruleset_version="1.0.0")

    assert run.status is RunStatus.COMPLETED_WITH_ERRORS
    assert [result.finding_code for result in run.results] == ["UNQA-V001"]
    assert run.errors[0].component == "UNQA-V002"
    assert run.errors[0].recoverable is True
~~~

- [ ] **Step 2: Run the test to verify it fails**

Run: uv run pytest tests/engine/test_runner.py -v

Expected: FAIL with ModuleNotFoundError for un_schema_qa.engine.runner.

- [ ] **Step 3: Implement ValidationEngine**

~~~python
# src/un_schema_qa/engine/runner.py
from collections.abc import Callable
from datetime import UTC, datetime

from un_schema_qa.engine.registry import ValidatorRegistry
from un_schema_qa.models.enums import RunStatus
from un_schema_qa.models.project import ValidationProject
from un_schema_qa.models.results import (
    CheckResult,
    RunError,
    RunMetadata,
    ValidationRun,
)


class ValidationEngine:
    def __init__(
        self,
        registry: ValidatorRegistry,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._registry = registry
        self._clock = clock or (lambda: datetime.now(UTC))

    def run(
        self,
        project: ValidationProject,
        run_id: str,
        ruleset_version: str,
    ) -> ValidationRun:
        results: list[CheckResult] = []
        errors: list[RunError] = []
        succeeded = 0
        validators = self._registry.ordered()

        for validator in validators:
            try:
                results.extend(validator.validate(project))
                succeeded += 1
            except Exception as exc:
                errors.append(
                    RunError(
                        category="validator_execution",
                        code="ENGINE_VALIDATOR_FAILURE",
                        message=str(exc),
                        component=validator.code,
                        recoverable=True,
                    )
                )

        if errors and validators and succeeded == 0:
            status = RunStatus.FAILED
        elif errors:
            status = RunStatus.COMPLETED_WITH_ERRORS
        else:
            status = RunStatus.COMPLETED

        ordered_results = tuple(
            sorted(
                results,
                key=lambda result: (
                    result.finding_code,
                    result.dataset or "",
                    result.field or "",
                    result.domain or "",
                ),
            )
        )
        return ValidationRun(
            metadata=RunMetadata(
                run_id=run_id,
                started_at=self._clock(),
                ruleset_version=ruleset_version,
                profile_version=project.profile.version,
            ),
            status=status,
            results=ordered_results,
            errors=tuple(errors),
        )
~~~

~~~python
# src/un_schema_qa/engine/__init__.py
"""Deterministic validation engine."""

from un_schema_qa.engine.runner import ValidationEngine

__all__ = ["ValidationEngine"]
~~~

- [ ] **Step 4: Run the complete Phase 1 verification suite**

Run: uv run pytest -v && uv run ruff check . && uv run mypy && uv build

Expected: All tests pass, Ruff and Mypy exit 0, and uv build creates both wheel and source distribution under dist.

- [ ] **Step 5: Commit**

~~~bash
git add src/un_schema_qa/engine tests/engine/test_runner.py
git commit -m "feat: run validators with error isolation"
~~~

## Phase 1 Completion Gate

Run all commands from a clean checkout:

~~~bash
uv sync --all-groups
uv lock --check
uv run pytest --cov=un_schema_qa --cov-report=term-missing
uv run ruff check .
uv run mypy
uv build
~~~

Expected:

- The lockfile is current.
- All Phase 1 tests pass.
- Coverage lists every Phase 1 module with no untested public method.
- Ruff exits 0.
- Mypy exits 0 in strict mode.
- dist contains one wheel and one source distribution for version 0.1.0.
- git status --short prints no output.
