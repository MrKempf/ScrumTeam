"""Implementation of the agentic Scrum team orchestration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, cast

from . import best_practices
from .document_reader import extract_keywords, read_requirements
from .roles import TEAM_TEMPLATE, Architect, Developer, Tester


def _format_output(payload: object) -> str:
    """Return a stable string representation of payloads for the activity log."""

    if isinstance(payload, str):
        return payload
    try:
        return json.dumps(payload, indent=2, sort_keys=True)
    except TypeError:
        return str(payload)


@dataclass
class ScrumTeam:
    """Agentic Scrum team coordinating multiple specialist roles."""

    architect: Architect
    developers: Sequence[Developer]
    testers: Sequence[Tester]
    practices: Dict[str, List[str]]

    @classmethod
    def default(cls) -> "ScrumTeam":
        template = TEAM_TEMPLATE
        return cls(
            architect=template["architect"],
            developers=template["developers"],
            testers=template["testers"],
            practices=template["best_practices"],
        )

    def run_iteration(self, requirement_file: str | Path) -> Dict[str, object]:
        requirements = read_requirements(requirement_file)
        if not requirements:
            raise ValueError("Requirement document must contain at least one requirement line.")

        keywords = extract_keywords(requirements)

        logs: List[Dict[str, str]] = []
        logs.append(
            {
                "speaker": "Scrum Master",
                "prompt": f"Share requirements sourced from {requirement_file}.",
                "response": _format_output(requirements),
            }
        )

        architecture = self.architect.produce_architecture(requirements, keywords)
        logs.append(
            {
                "speaker": self.architect.name,
                "prompt": "Provide architecture guidance for the upcoming sprint.",
                "response": _format_output(architecture),
            }
        )

        implementation_plans: List[Dict[str, List[str]]] = []
        for developer in self.developers:
            plan = developer.create_implementation_plan(requirements, architecture)
            developer.review_code(plan)
            implementation_plans.append(plan)
            logs.append(
                {
                    "speaker": developer.name,
                    "prompt": "Draft implementation plan aligned with the architecture and requirements.",
                    "response": _format_output(plan),
                }
            )

        test_plans: List[Dict[str, List[str]]] = []
        for tester in self.testers:
            tester_plan = tester.create_test_plan(requirements, architecture)
            test_plans.append(tester_plan)
            logs.append(
                {
                    "speaker": tester.name,
                    "prompt": "Outline validation strategy covering functional and non-functional needs.",
                    "response": _format_output(tester_plan),
                }
            )

        result = {
            "requirements": requirements,
            "keywords": keywords,
            "architecture": architecture,
            "implementation_plans": implementation_plans,
            "test_plans": test_plans,
            "best_practices": best_practices.all_best_practices(),
            "quality_assurance": {
                "code_review": "All developer outputs include mandatory peer review checklists.",
                "testing": "Test plans align with automated and exploratory coverage for every requirement.",
            },
            "logs": logs,
        }

        return result

    def handle_follow_up(self, result: Dict[str, object], instruction: str) -> Dict[str, Iterable[str]]:
        """Apply a post-sprint instruction and capture how each role reacts."""

        logs = cast(List[Dict[str, str]], result.setdefault("logs", []))
        logs.append(
            {
                "speaker": "Product Owner",
                "prompt": "Provide additional instruction after sprint review.",
                "response": instruction,
            }
        )

        architecture_note = self.architect.respond_to_instruction(instruction)
        logs.append(
            {
                "speaker": self.architect.name,
                "prompt": "Acknowledge follow-up instruction and adapt architecture guidance.",
                "response": architecture_note,
            }
        )

        developer_notes: List[str] = []
        for developer, plan in zip(self.developers, result.get("implementation_plans", [])):
            note = developer.respond_to_instruction(instruction)
            developer_notes.append(note)
            logs.append(
                {
                    "speaker": developer.name,
                    "prompt": "Adjust implementation approach based on new instruction.",
                    "response": note,
                }
            )
            if isinstance(plan, dict):
                follow_up_actions = plan.setdefault("follow_up_actions", [])
                if isinstance(follow_up_actions, list):
                    follow_up_actions.append(note)

        tester_notes: List[str] = []
        for tester, plan in zip(self.testers, result.get("test_plans", [])):
            note = tester.respond_to_instruction(instruction)
            tester_notes.append(note)
            logs.append(
                {
                    "speaker": tester.name,
                    "prompt": "Adapt validation strategy for follow-up instruction.",
                    "response": note,
                }
            )
            if isinstance(plan, dict):
                follow_up_actions = plan.setdefault("follow_up_actions", [])
                if isinstance(follow_up_actions, list):
                    follow_up_actions.append(note)

        follow_up = {
            "instruction": instruction,
            "architecture": architecture_note,
            "development": developer_notes,
            "testing": tester_notes,
        }

        cast(List[Dict[str, Iterable[str]]], result.setdefault("follow_ups", [])).append(follow_up)

        return follow_up


def summarize_iteration(result: Dict[str, object]) -> str:
    """Produce a human-friendly summary of the iteration output."""
    lines: List[str] = []
    lines.append("=== Requirements ===")
    for requirement in result["requirements"]:
        lines.append(f"- {requirement}")

    lines.append("\n=== Architecture Decisions ===")
    architecture: Dict[str, str] = result["architecture"]  # type: ignore[assignment]
    for key, value in architecture.items():
        lines.append(f"{key.title()}: {value}")

    lines.append("\n=== Implementation Plans ===")
    for index, plan in enumerate(result["implementation_plans"], start=1):
        lines.append(f"Developer {index} plan:")
        for task in plan.get("tasks", []):
            lines.append(f"  * {task}")
        for review_note in plan.get("review_notes", []):
            lines.append(f"  - Review: {review_note}")

    lines.append("\n=== Test Strategies ===")
    for index, plan in enumerate(result["test_plans"], start=1):
        lines.append(f"Tester {index} plan:")
        for strategy in plan.get("strategy", []):
            lines.append(f"  * {strategy}")
        for test in plan.get("tests", []):
            lines.append(f"  - Test: {test}")

    lines.append("\n=== Best Practices Checklist ===")
    for practice in result["best_practices"]:
        lines.append(f"- {practice}")

    lines.append("\n=== Quality Assurance Guardrails ===")
    qa: Dict[str, str] = result["quality_assurance"]  # type: ignore[assignment]
    for topic, note in qa.items():
        lines.append(f"{topic.title()}: {note}")

    follow_ups = cast(Iterable[Dict[str, object]], result.get("follow_ups", []))
    if follow_ups:
        lines.append("\n=== Follow-up Instructions ===")
        for index, follow_up in enumerate(follow_ups, start=1):
            lines.append(f"Instruction {index}: {follow_up['instruction']}")
            lines.append(f"  - Architecture: {follow_up['architecture']}")
            for dev_note in follow_up.get("development", []):
                lines.append(f"  - Development: {dev_note}")
            for test_note in follow_up.get("testing", []):
                lines.append(f"  - Testing: {test_note}")

    logs = cast(Iterable[Dict[str, str]], result.get("logs", []))
    if logs:
        lines.append("\n=== Interaction Log ===")
        for entry in logs:
            lines.append(f"Speaker: {entry['speaker']}")
            lines.append(f"Prompt: {entry['prompt']}")
            lines.append(f"Response: {entry['response']}")

    return "\n".join(lines)
