from __future__ import annotations

from pathlib import Path

import pytest

from scrum_team.team import ScrumTeam, summarize_iteration


def write_requirements(tmp_path: Path) -> Path:
    path = tmp_path / "requirements.txt"
    path.write_text(
        "Real-time telemetry ingestion\n"
        "Secure data storage\n"
        "Responsive mobile app\n",
        encoding="utf-8",
    )
    return path


def test_run_iteration_generates_artifacts(tmp_path: Path) -> None:
    requirements_path = write_requirements(tmp_path)

    team = ScrumTeam.default()
    result = team.run_iteration(requirements_path)

    assert len(result["requirements"]) == 3
    assert result["architecture"]["pattern"] in {
        "event-driven",
        "layered-service",
        "microservices",
        "data-lakehouse",
    }
    assert len(result["implementation_plans"]) == len(team.developers)
    assert len(result["test_plans"]) == len(team.testers)

    for artifact in result["source_code"]:
        assert artifact["code"].count("dataclass") >= 1
        assert "FeatureContract" in artifact["code"]

    for unit_suite in result["unit_tests"]:
        assert unit_suite["tools"] == ["pytest", "coverage"]
        assert "@pytest.mark.parametrize" in unit_suite["code"]

    summary = summarize_iteration(result)
    assert "=== Requirements ===" in summary
    assert "=== Interaction Log ===" in summary


def test_follow_up_appends_actions(tmp_path: Path) -> None:
    team = ScrumTeam.default()
    result = team.run_iteration(write_requirements(tmp_path))

    follow_up = team.handle_follow_up(result, "Improve accessibility")

    assert follow_up["instruction"] == "Improve accessibility"
    assert any("accessibility" in note.lower() for note in follow_up["testing"])
    assert result["follow_ups"][0] == follow_up

    first_plan = result["implementation_plans"][0]
    assert any("accessibility" in note.lower() for note in first_plan["follow_up_actions"])


def test_configure_llm_providers_validates_length() -> None:
    team = ScrumTeam.default()

    with pytest.raises(ValueError):
        team.configure_llm_providers({"developers": ["openai:gpt-4o"]})


def test_configure_llm_providers_accepts_mixed_specs() -> None:
    team = ScrumTeam.default()

    team.configure_llm_providers(
        {
            "architect": {"provider": "ollama", "model": "llama3"},
            "developers": ["openai:gpt-4o-mini", {"provider": "ollama", "model": "llama3"}, "openai"],
            "testers": "ollama:llama3",
        }
    )

    assert team.architect.llm_provider.provider == "ollama"
    assert team.architect.llm_provider.deployment == "local"
    assert {developer.llm_provider.provider for developer in team.developers} == {
        "openai",
        "ollama",
    }
