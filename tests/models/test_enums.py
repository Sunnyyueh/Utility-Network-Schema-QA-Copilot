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
