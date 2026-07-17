# Utility Network Schema QA Copilot Design

**Date:** 2026-07-16  
**Status:** Approved for implementation planning  
**License:** Apache License 2.0

## 1. Purpose

Utility Network Schema QA Copilot is an open-source, AI-assisted validation system for water, wastewater, and stormwater schema mappings. It helps utilities, municipalities, engineering firms, GIS teams, and migration specialists identify schema and mapping risks before data loading begins.

The product combines two layers:

1. A deterministic Python validation engine that is the sole authority for check outcomes.
2. A retrieval-augmented AI assistant that explains validated findings, cites public guidance, and recommends review steps.

The AI layer cannot create, delete, reclassify, or override validation results.

## 2. Product Outcomes

The system is designed to:

- Detect schema and mapping risks before migration or loading.
- Standardize QA/QC practices across teams and projects.
- Convert specialist review practices into reusable, versioned rules.
- Produce repeatable and independently reviewable reports.
- Preserve institutional knowledge through documented utility profiles.
- Support both human users and compatible AI agents.
- Operate without ArcGIS Pro, ArcPy, or a language-model API key.
- Provide machine-readable outputs for pipelines, dashboards, and governance.

## 3. Intended Users

- Municipal water and sewer utilities.
- Stormwater and drainage programs.
- Utility Network implementation teams.
- GIS analysts and developers.
- Civil and environmental engineering firms.
- Data migration and ETL teams.
- QA/QC managers.
- Infrastructure consultants.
- Students and researchers studying utility modernization.

## 4. Design Principles

### 4.1 Deterministic Before Generative

All pass, warning, fail, and blocker outcomes originate from versioned Python rules. A language model may explain a result but cannot determine or alter it.

### 4.2 Offline Core

Parsing, normalization, validation, reporting, and evidence-manifest generation work without network access or an AI provider.

### 4.3 Read-Only Operation

Version 1 reads schema metadata and mapping configuration. It does not modify source files, write to databases, run migrations, or perform reconcile/post operations.

### 4.4 Public and Portable

The core accepts CSV, Excel, JSON, and YAML inputs and does not require proprietary GIS software.

### 4.5 Evidence and Reproducibility

Every run records the input hashes, ruleset version, profile version, software version, configuration, timestamps, output hashes, and optional model metadata required to reproduce or audit the result.

### 4.6 Bounded Complexity

Each component has a single responsibility and a documented interface. Advanced capabilities belong in later releases when they require production database access, geometry processing, or migration execution.

## 5. System Architecture

~~~text
CLI / Python API / Web Application / MCP / Agent Skill
                         |
                         v
                 Agent Orchestrator
                    /          \
                   v            v
        Deterministic Core    Knowledge Retrieval
            /       \              |
           v         v             v
    Canonical Model  Profiles   Cited Guidance
            \       /              |
             v     v               |
          Validation Findings <----+
                   |
                   v
        Evidence and Report Layer
                   |
                   v
       JSON / CSV / Markdown / HTML
~~~

## 6. Component Boundaries

### 6.1 Input Intake

Responsibilities:

- Accept CSV, XLSX, JSON, and YAML.
- Validate file type, size, encoding, workbook shape, and required sheets.
- Reject unsafe paths, unsupported archives, and malformed files.
- Convert input-specific errors into structured runtime errors.

Dependencies:

- Python standard library.
- Pandas and OpenPyXL for tabular formats.
- PyYAML for YAML.

### 6.2 Canonical Model

Responsibilities:

- Normalize every supported format into a stable internal representation.
- Preserve source locations so findings can point back to a file, sheet, row, and column.
- Separate raw input from normalized values.

Primary models:

- **ValidationProject**
- **DatasetDefinition**
- **FieldDefinition**
- **MappingRule**
- **TransformationDefinition**
- **DomainDefinition**
- **DomainCode**
- **SubtypeDefinition**
- **AssetClassification**
- **UtilityProfile**
- **RuleConfiguration**

Pydantic v2 models provide validation, serialization, and JSON schema generation.

### 6.3 Utility Profiles

The repository contains three versioned profiles:

- Water distribution.
- Wastewater collection.
- Stormwater and drainage.

Each profile defines:

- Domain terminology.
- Expected asset categories.
- Classification constraints.
- Severity overrides.
- Rule configuration.
- Review guidance.

Profiles extend shared rules and cannot execute arbitrary code.

### 6.4 Deterministic Validation Engine

Responsibilities:

- Select the base rules, utility profile, and project overrides.
- Execute validators in a stable order.
- Isolate a failing validator without discarding successful results.
- Produce structured **CheckResult** records.
- Generate deterministic output for the same normalized input and ruleset.

The engine does not call a language model or retrieval service.

### 6.5 Knowledge Retrieval

Responsibilities:

- Ingest approved public documents and project documentation.
- Store title, publisher, canonical URL, publication date, retrieval date, and content hash.
- Perform hybrid keyword and optional vector retrieval.
- Return text excerpts with citations.
- Refuse to treat uncited content as authoritative guidance.

SQLite FTS5 provides offline keyword search. Optional embeddings improve ranking but are not required for core operation.

### 6.6 Agent Orchestrator

Responsibilities:

- Interpret user intent.
- Select read-only validation and retrieval tools.
- Explain existing findings.
- Produce structured executive and technical summaries.
- Record provider, model, prompt version, and citations.

The orchestrator cannot mutate input files or validation results.

### 6.7 Report and Evidence Layer

Responsibilities:

- Write the canonical JSON result first.
- Render CSV, Markdown, and HTML independently.
- Produce an evidence manifest.
- Include finding codes, rule versions, locations, expected values, actual values, and remediation categories.
- Compute output hashes after rendering.

## 7. End-to-End Data Flow

1. The user selects water, wastewater, or stormwater.
2. The user supplies source schema, target schema, mapping, domain, and asset-classification files.
3. Input Intake validates and parses each file.
4. The Canonical Model normalizes the parsed content.
5. The engine combines base rules, the selected utility profile, and permitted project overrides.
6. Validators emit ordered **CheckResult** records.
7. The canonical JSON result and evidence manifest are written.
8. If requested, Knowledge Retrieval finds cited guidance for relevant finding codes.
9. If an AI provider is configured, the Agent Orchestrator explains the findings using the structured result and retrieved citations.
10. Report renderers produce CSV, Markdown, and HTML.
11. CLI, Python, Web, MCP, and Agent Skill interfaces return or expose the same underlying result.

## 8. Validation Result Model

Each check produces a **CheckResult** with:

- finding_code
- rule_version
- status
- severity_rank
- profile
- dataset
- field
- domain
- source_location
- expected
- actual
- evidence
- remediation_category
- remediation_guidance

Allowed status values:

- **PASS**: The checked condition is satisfied.
- **WARNING**: The workflow may continue, but human review is recommended.
- **FAIL**: The mapping or schema violates the rule.
- **BLOCKER**: The issue should be resolved before migration proceeds.

Reports may hide PASS results by default, but the canonical JSON retains them for auditability.

## 9. Version 1 Validation Rules

| Code | Rule |
| --- | --- |
| **UNQA-V001** | Required input columns |
| **UNQA-V002** | Duplicate source-field mappings |
| **UNQA-V003** | Duplicate target-field mappings |
| **UNQA-V004** | Unmapped required target fields |
| **UNQA-V005** | Unknown dataset references |
| **UNQA-V006** | Unknown field references |
| **UNQA-V007** | Data-type compatibility |
| **UNQA-V008** | String-length and truncation risk |
| **UNQA-V009** | Nullability, defaults, and required-value coverage |
| **UNQA-V010** | Coded-value domain coverage |
| **UNQA-V011** | Duplicate or conflicting domain codes |
| **UNQA-V012** | Subtype compatibility |
| **UNQA-V013** | Asset-group and asset-type pair validity |
| **UNQA-V014** | Missing transformation definitions |
| **UNQA-V015** | One-to-many and many-to-one mapping conflicts |
| **UNQA-V016** | Ignored and unused source-field documentation |
| **UNQA-V017** | Profile terminology and classification checks |
| **UNQA-V018** | Cross-file reference consistency |

Every rule requires documentation, pass fixtures, failure fixtures, edge-case fixtures, remediation guidance, and a stable output contract.

## 10. Runtime Error Model

Runtime errors are separate from validation outcomes.

Run status values:

- **completed**
- **completed_with_errors**
- **failed**

Error categories:

| Category | Behavior |
| --- | --- |
| Malformed file | Stop processing that file and identify the parse location |
| Missing required columns | Reject the affected input without guessing field meaning |
| Invalid row | Isolate the row and continue when the canonical model remains valid |
| Validator exception | Mark the rule incomplete and continue independent validators |
| Retrieval unavailable | Preserve findings and omit unsupported guidance |
| AI provider unavailable | Produce the complete deterministic report without AI |
| Renderer failure | Preserve canonical JSON and retry formats independently |
| MCP interruption | Return a structured protocol error without mutating state |
| Web-session interruption | Delete session files and allow a clean rerun |

## 11. Security and Privacy

- Treat all uploaded text as data, never as instructions.
- Expose only allowlisted read-only tools to the agent.
- Do not provide shell, arbitrary code execution, database-write, migration, or reconcile/post tools.
- Read API keys only from environment variables or a supported secret manager.
- Do not log keys, source-file content, or sensitive local paths.
- Send structured findings rather than complete workbooks to AI providers by default.
- Escape spreadsheet formula prefixes in generated tabular reports.
- Enforce file, workbook, sheet, row, and column limits.
- Protect against path traversal, unsafe archives, malformed encodings, and oversized inputs.
- Delete web-session uploads after the session.
- Record hashes for auditability without copying source content into the evidence manifest.

## 12. Interfaces

### 12.1 Python API

Provides typed project construction, validation, result inspection, and report export.

### 12.2 CLI

Provides commands for:

- Inspecting input structure.
- Validating a project.
- Explaining an existing report.
- Searching guidance.
- Serving the MCP interface.
- Printing version and profile information.

### 12.3 Web Application

Provides:

- Profile selection.
- Guided uploads.
- Deterministic validation.
- Finding filters.
- AI explanations.
- Report downloads.

### 12.4 MCP Server

Exposes:

- **inspect_schema**
- **compare_schemas**
- **validate_mapping**
- **validate_required_fields**
- **validate_domains**
- **validate_asset_classifications**
- **summarize_findings**
- **generate_qa_report**
- **search_utility_guidance**
- **explain_finding**

### 12.5 Agent Skill

The skill instructs compatible agents to:

- Select an appropriate profile.
- Inspect inputs before validation.
- Use deterministic tools for conclusions.
- Distinguish findings from AI recommendations.
- Cite guidance.
- Generate an evidence manifest.
- Avoid input mutation.

## 13. Technology Baseline

- Python 3.12
- Pydantic v2
- Pandas
- OpenPyXL
- PyYAML
- Typer
- Rich
- Pydantic AI
- SQLite FTS5
- FastMCP
- Streamlit
- Jinja2
- Pytest
- Hypothesis
- Ruff
- Mypy
- GitHub Actions

Dependency versions are pinned through the package lock strategy selected in the implementation plan.

## 14. Testing Strategy

### 14.1 Parser Tests

Cover supported formats, missing values, malformed inputs, encoding problems, and workbook-shape errors.

### 14.2 Validator Tests

Every finding code has pass, fail or warning, and edge-case coverage.

### 14.3 Property-Based Tests

Exercise field order, duplicate rows, empty values, random domain codes, and serialization round trips.

### 14.4 Profile Contract Tests

Ensure all utility profiles conform to the same profile schema and shared rule contracts.

### 14.5 Golden Report Tests

Ensure fixed inputs produce stable JSON, CSV, Markdown, and HTML reports.

### 14.6 Agent Tests

Ensure structured AI output cannot alter finding codes, statuses, or rule evidence.

### 14.7 Retrieval Tests

Ensure authoritative guidance includes citations and uncited content is not represented as authoritative.

### 14.8 MCP Contract Tests

Validate tool schemas, read-only behavior, success responses, and structured errors.

### 14.9 Integration and Security Tests

Cover offline CLI execution, formula injection, path traversal, oversized inputs, prompt injection, secret redaction, and web-session cleanup.

### 14.10 Reproducibility Tests

Ensure the same input, configuration, profile, and ruleset produce the same findings and stable hashes, excluding explicitly documented runtime timestamps.

## 15. Version 1 Deliverables

- Installable Python package.
- Typed Python API.
- Complete CLI.
- Three utility profiles.
- Eighteen validation rules.
- JSON, CSV, Markdown, and HTML reports.
- Evidence manifest.
- Hybrid retrieval.
- OpenAI-compatible and Ollama/local adapters.
- AI explanation agent.
- Streamlit demo.
- MCP server.
- Agent skill.
- Water, wastewater, and stormwater examples.
- Architecture, API, rules, security, and contribution documentation.
- CI, package build, and release automation.

## 16. Version 1 Non-Goals

- ArcPy or ArcGIS Pro integration.
- Direct enterprise-geodatabase access.
- Geometry, topology, or dirty-area validation.
- ETL or migration execution.
- Reconcile/post.
- Production database writes.
- Multi-agent collaboration.
- Client-specific or confidential schemas.

These capabilities may be considered for version 1.1 through version 2 after the read-only core is stable.

## 17. Completion Criteria

Version 1 is complete only when:

- The core runs without an AI key.
- Every public CLI command has integration coverage.
- Every finding code has documentation and tests.
- Deterministic tests, lint, type checking, and package build pass.
- Authoritative retrieval output includes citations.
- MCP and Agent Skill use the same validation core as the CLI and Python API.
- Each utility profile includes an example input and complete report set.
- Every capability described as complete in the README has corresponding code or a verifiable artifact.
- A release can be installed and executed in a clean environment.

## 18. Commit and Release Strategy

Implementation is divided into cohesive, reviewable commits across project foundation, models, parsers, validators, profiles, reports, retrieval, agent orchestration, interfaces, documentation, CI, and release engineering.

The project may exceed 50 commits, but commit count is never padded. Every commit must:

- Represent a meaningful functional, testing, documentation, or governance increment.
- Use a clear conventional commit message.
- Avoid empty or whitespace-only changes.
- Include relevant tests or documentation when applicable.
- Preserve a reviewable history of how the system developed.

Releases follow semantic versioning and publish release notes generated from verified changes.

## 19. Documentation and Public Evidence

Public artifacts include:

- Source code and commit history.
- Versioned rules and profiles.
- Example inputs and reports.
- Test and CI results.
- Documentation and tutorials.
- Releases and package metadata.
- Issues, discussions, and external contributions when they occur.

The project does not claim adoption, performance improvements, or external validation without corresponding independent evidence.

