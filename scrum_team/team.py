"""Implementation of the agentic Scrum team orchestration."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Union, cast

from . import best_practices
from .document_reader import extract_keywords, read_requirements
from .roles import LLMProviderSpec, TEAM_TEMPLATE, Architect, Developer, Role, Tester


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

    def configure_llm_providers(
        self,
        providers: Mapping[str, Union[LLMProviderSpec, Sequence[LLMProviderSpec]]],
    ) -> None:
        """Assign LLM providers to the architect, developers, and testers.

        ``providers`` accepts the following structure::

            {
                "architect": "openai:gpt-4o",
                "developers": ["openai:gpt-4o-mini", "ollama:llama3", ...],
                "testers": "ollama:llama3",
            }

        Single values apply to every member of that discipline. A sequence must match the
        number of developers or testers respectively.
        """

        if "architect" in providers:
            self.architect.set_llm_provider(providers["architect"])

        if "developers" in providers:
            developer_config = providers["developers"]
            self._apply_role_provider(self.developers, developer_config)

        if "testers" in providers:
            tester_config = providers["testers"]
            self._apply_role_provider(self.testers, tester_config)

    @staticmethod
    def _apply_role_provider(
        roles: Sequence[Role],
        config: Union[LLMProviderSpec, Sequence[LLMProviderSpec]],
    ) -> None:
        if isinstance(config, Sequence) and not isinstance(config, (str, bytes)):
            if len(config) != len(roles):
                raise ValueError(
                    "Provider configuration length must match the number of roles in the discipline."
                )
            for role, role_config in zip(roles, config):
                role.set_llm_provider(role_config)
        else:
            for role in roles:
                role.set_llm_provider(config)

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
        source_code_artifacts: List[Dict[str, Any]] = []
        unit_test_artifacts: List[Dict[str, Any]] = []
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
            source_code = developer.produce_source_code(requirements, architecture)
            source_code_artifacts.append(source_code)
            logs.append(
                {
                    "speaker": developer.name,
                    "prompt": "Produce source code scaffold that realises the implementation plan.",
                    "response": _format_output(source_code),
                }
            )
            unit_tests = developer.produce_unit_tests(requirements, architecture)
            unit_test_artifacts.append(unit_tests)
            logs.append(
                {
                    "speaker": developer.name,
                    "prompt": "Deliver unit tests paired with the implementation work.",
                    "response": _format_output(unit_tests),
                }
            )

        test_plans: List[Dict[str, List[str]]] = []
        test_scripts: List[Dict[str, Any]] = []
        test_summaries: List[Dict[str, str]] = []
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
            tester_script = tester.create_test_script(requirements, architecture)
            test_scripts.append(tester_script)
            logs.append(
                {
                    "speaker": tester.name,
                    "prompt": "Provide executable test scripts supporting the plan.",
                    "response": _format_output(tester_script),
                }
            )
            tester_summary = tester.summarize_testing(requirements, architecture)
            test_summaries.append(tester_summary)
            logs.append(
                {
                    "speaker": tester.name,
                    "prompt": "Summarise anticipated testing outcomes and risks.",
                    "response": _format_output(tester_summary),
                }
            )

        result = {
            "requirements": requirements,
            "keywords": keywords,
            "architecture": architecture,
            "adr_decisions": architecture.get("adr_records", []),
            "implementation_plans": implementation_plans,
            "source_code": source_code_artifacts,
            "unit_tests": unit_test_artifacts,
            "test_plans": test_plans,
            "test_scripts": test_scripts,
            "test_summaries": test_summaries,
            "best_practices": best_practices.all_best_practices(),
            "quality_assurance": {
                "code_review": "All developer outputs include mandatory peer review checklists.",
                "testing": "Test plans, scripts, and summaries align with automated and exploratory coverage for every requirement.",
            },
            "llm_providers": {
                "architect": self.architect.llm_provider.as_dict(),
                "developers": [developer.llm_provider.as_dict() for developer in self.developers],
                "testers": [tester.llm_provider.as_dict() for tester in self.testers],
            },
            "llm_providers": {
                "architect": self.architect.llm_provider.as_dict(),
                "developers": [developer.llm_provider.as_dict() for developer in self.developers],
                "testers": [tester.llm_provider.as_dict() for tester in self.testers],
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

        implementation_plans = cast(List[Dict[str, Any]], result.get("implementation_plans", []))
        source_code_entries = cast(List[Dict[str, Any]], result.get("source_code", []))
        unit_test_entries = cast(List[Dict[str, Any]], result.get("unit_tests", []))

        developer_notes: List[str] = []
        for index, developer in enumerate(self.developers):
            plan: Dict[str, Any] = implementation_plans[index] if index < len(implementation_plans) else {}
            note = developer.respond_to_instruction(instruction)
            developer_notes.append(note)
            logs.append(
                {
                    "speaker": developer.name,
                    "prompt": "Adjust implementation approach based on new instruction.",
                    "response": note,
                }
            )
            follow_up_actions = plan.setdefault("follow_up_actions", [])
            if isinstance(follow_up_actions, list):
                follow_up_actions.append(note)

            if index < len(source_code_entries):
                code_entry = source_code_entries[index]
                if isinstance(code_entry, dict):
                    code_notes = code_entry.setdefault("follow_up_notes", [])
                    if isinstance(code_notes, list):
                        code_notes.append(note)

            if index < len(unit_test_entries):
                test_entry = unit_test_entries[index]
                if isinstance(test_entry, dict):
                    test_notes = test_entry.setdefault("follow_up_notes", [])
                    if isinstance(test_notes, list):
                        test_notes.append(note)

        test_plans = cast(List[Dict[str, Any]], result.get("test_plans", []))
        test_scripts = cast(List[Dict[str, Any]], result.get("test_scripts", []))
        test_summaries = cast(List[Dict[str, Any]], result.get("test_summaries", []))

        tester_notes: List[str] = []
        for index, tester in enumerate(self.testers):
            plan = test_plans[index] if index < len(test_plans) else {}
            note = tester.respond_to_instruction(instruction)
            tester_notes.append(note)
            logs.append(
                {
                    "speaker": tester.name,
                    "prompt": "Adapt validation strategy for follow-up instruction.",
                    "response": note,
                }
            )
            follow_up_actions = plan.setdefault("follow_up_actions", [])
            if isinstance(follow_up_actions, list):
                follow_up_actions.append(note)

            if index < len(test_scripts):
                script_entry = test_scripts[index]
                if isinstance(script_entry, dict):
                    script_notes = script_entry.setdefault("follow_up_notes", [])
                    if isinstance(script_notes, list):
                        script_notes.append(note)

            if index < len(test_summaries):
                summary_entry = test_summaries[index]
                if isinstance(summary_entry, dict):
                    summary_notes = summary_entry.setdefault("follow_up_notes", [])
                    if isinstance(summary_notes, list):
                        summary_notes.append(note)

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
    architecture: Dict[str, Any] = result["architecture"]  # type: ignore[assignment]
    for key, value in architecture.items():
        if key == "adr_records":
            continue
        lines.append(f"{key.title()}: {value}")

    provider_info = result.get("llm_providers")
    if isinstance(provider_info, dict):
        lines.append("\n=== LLM Provider Assignments ===")

        def describe(entry: object) -> str:
            if isinstance(entry, dict):
                provider_name = str(entry.get("provider") or entry.get("name") or "unknown")
                deployment = entry.get("deployment") or entry.get("location")
                model = entry.get("model")
                detail = f"{provider_name}"
                if deployment:
                    detail += f" ({deployment})"
                if model:
                    detail += f" model={model}"
                return detail
            return str(entry)

        architect_provider = provider_info.get("architect")
        if architect_provider:
            lines.append(f"Architect: {describe(architect_provider)}")

        for index, provider in enumerate(provider_info.get("developers", []), start=1):
            lines.append(f"Developer {index}: {describe(provider)}")

        for index, provider in enumerate(provider_info.get("testers", []), start=1):
            lines.append(f"Tester {index}: {describe(provider)}")

    lines.append("\n=== Implementation Plans ===")
    for index, plan in enumerate(result["implementation_plans"], start=1):
        lines.append(f"Developer {index} plan:")
        for task in plan.get("tasks", []):
            lines.append(f"  * {task}")
        for review_note in plan.get("review_notes", []):
            lines.append(f"  - Review: {review_note}")

    source_code_entries = cast(Iterable[Dict[str, Any]], result.get("source_code", []))
    if source_code_entries:
        lines.append("\n=== Source Code Deliverables ===")
        for entry in source_code_entries:
            module = entry.get("module", "module.py")
            owner = entry.get("owner", "Developer")
            summary = entry.get("summary")
            lines.append(f"{module} (owner: {owner})")
            if summary:
                lines.append(f"  - Summary: {summary}")

    unit_test_entries = cast(Iterable[Dict[str, Any]], result.get("unit_tests", []))
    if unit_test_entries:
        lines.append("\n=== Unit Test Suites ===")
        for entry in unit_test_entries:
            module = entry.get("module", "test_module.py")
            owner = entry.get("owner", "Developer")
            summary = entry.get("summary")
            lines.append(f"{module} (owner: {owner})")
            if summary:
                lines.append(f"  - Summary: {summary}")
            tools = entry.get("tools", [])
            if tools:
                lines.append(f"  - Tools: {', '.join(tools)}")

    lines.append("\n=== Test Strategies ===")
    for index, plan in enumerate(result["test_plans"], start=1):
        lines.append(f"Tester {index} plan:")
        for strategy in plan.get("strategy", []):
            lines.append(f"  * {strategy}")
        for test in plan.get("tests", []):
            lines.append(f"  - Test: {test}")

    test_scripts = cast(Iterable[Dict[str, Any]], result.get("test_scripts", []))
    if test_scripts:
        lines.append("\n=== Test Scripts ===")
        for entry in test_scripts:
            owner = entry.get("owner", "Tester")
            lines.append(f"Script owner: {owner}")
            for step in entry.get("steps", []):
                lines.append(f"  * {step}")
            tooling = entry.get("tooling")
            if tooling:
                lines.append(f"  - Tooling: {', '.join(tooling)}")

    test_summaries = cast(Iterable[Dict[str, str]], result.get("test_summaries", []))
    if test_summaries:
        lines.append("\n=== Test Summaries ===")
        for entry in test_summaries:
            owner = entry.get("owner", "Tester")
            lines.append(f"Summary owner: {owner}")
            for key in ("coverage", "risks", "next_steps"):
                value = entry.get(key)
                if value:
                    lines.append(f"  - {key.replace('_', ' ').title()}: {value}")

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
