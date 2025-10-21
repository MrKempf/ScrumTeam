from __future__ import annotations

from pathlib import Path
import json

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

    artifact_dir = Path(result["artifact_directory"])
    assert artifact_dir.exists()
    snapshot = (artifact_dir / "requirements_snapshot.txt").read_text(encoding="utf-8").strip()
    assert "Real-time telemetry ingestion" in snapshot
    history_file = artifact_dir.parent / "history.json"
    assert history_file.exists()
    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert history[0]["sprint_number"] == 1
    for artifact in result["source_code"]:
        assert (artifact_dir / "source" / artifact["module"]).exists()
    for unit_suite in result["unit_tests"]:
        assert (artifact_dir / "tests" / unit_suite["module"]).exists()


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


def test_new_sprint_considers_previous_artifacts(tmp_path: Path) -> None:
    requirements_path = write_requirements(tmp_path)

    team = ScrumTeam.default()
    first_result = team.run_iteration(requirements_path)
    assert first_result["previous_artifacts"] == []

    new_team = ScrumTeam.default()
    second_result = new_team.run_iteration(requirements_path)
    assert second_result["sprint_number"] == 2
    assert len(second_result["previous_artifacts"]) == 1
    previous_entry = second_result["previous_artifacts"][0]
    assert previous_entry["sprint_number"] == 1
    assert Path(previous_entry["artifact_directory"]).exists()
