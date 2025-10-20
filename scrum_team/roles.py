"""Role definitions for the Scrum-based agentic AI team."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from .best_practices import BEST_PRACTICES


@dataclass
class Role:
    """Base class for all roles."""

    name: str
    focus_areas: List[str]
    responsibilities: List[str]

    def summarize(self) -> str:
        return f"{self.name}: focus on {', '.join(self.focus_areas)}"

    def respond_to_instruction(self, instruction: str) -> str:
        """Describe how the role will react to an additional instruction."""

        return f"{self.name} acknowledges instruction '{instruction}' and will incorporate it into upcoming work."


@dataclass
class Architect(Role):
    """Architect responsible for architecture decisions."""

    def produce_architecture(self, requirements: Iterable[str], keywords: Iterable[str]) -> Dict[str, str]:
        keyword_set = {keyword.lower() for keyword in keywords}
        pattern = "layered-service"
        if {"realtime", "latency"} & keyword_set:
            pattern = "event-driven"
        elif {"scalable", "microservice", "distributed"} & keyword_set:
            pattern = "microservices"
        elif {"analytics", "pipeline", "data"} & keyword_set:
            pattern = "data-lakehouse"

        critical_quality = "security" if "security" in keyword_set else "reliability"

        architecture = {
            "pattern": pattern,
            "critical_quality": critical_quality,
            "decisions": (
                "Adopt a {pattern} architecture emphasizing {quality}. Ensure services expose "
                "contract-first APIs with versioning and automated governance."
            ).format(pattern=pattern, quality=critical_quality),
            "adr_process": "Capture each decision in ADRs stored with the codebase.",
            "governance": (
                "Architect collaborates with developers to review design diagrams before coding."
            ),
        }
        return architecture

    def respond_to_instruction(self, instruction: str) -> str:  # noqa: D401 - see base
        return (
            f"{self.name} will update architecture guardrails to address: {instruction}. "
            "Any new decisions will be captured through ADRs for team visibility."
        )


@dataclass
class Developer(Role):
    """Developer responsible for implementation and code review."""

    skills: List[str] = field(default_factory=list)

    def create_implementation_plan(
        self,
        requirements: Iterable[str],
        architecture: Dict[str, str],
    ) -> Dict[str, List[str]]:
        plan: Dict[str, List[str]] = {
            "tasks": [],
            "code_review": [
                "Peer review all merge requests with checklists covering readability, testing, and security."
            ],
        }
        for requirement in requirements:
            plan["tasks"].append(
                f"Implement feature for: {requirement} aligned with {architecture['pattern']} pattern."
            )
        plan["tasks"].append("Integrate static analysis and continuous integration pipelines.")
        return plan

    def review_code(self, authored_plan: Dict[str, List[str]]) -> List[str]:
        comments = [
            "Verify unit tests exist for each feature module.",
            "Confirm adherence to coding standards and linting passes.",
            "Ensure threat modeling considerations are addressed in code.",
        ]
        authored_plan.setdefault("review_notes", []).extend(comments)
        return comments

    def respond_to_instruction(self, instruction: str) -> str:  # noqa: D401 - see base
        return (
            f"{self.name} will refine implementation tasks and tests to satisfy instruction: {instruction}. "
            "Updates will be paired with code review checklist adjustments."
        )


@dataclass
class Tester(Role):
    """Tester responsible for validation strategies."""

    specialties: List[str] = field(default_factory=list)

    def create_test_plan(
        self,
        requirements: Iterable[str],
        architecture: Dict[str, str],
    ) -> Dict[str, List[str]]:
        plan: Dict[str, List[str]] = {
            "strategy": [
                "Adopt test pyramid with unit, integration, contract, and exploratory testing.",
                f"Focus on validating {architecture['critical_quality']} risks early via automated suites.",
            ],
            "tests": [],
            "tooling": [
                "Integrate automated testing into CI/CD with parallel execution.",
                "Collect observability metrics to validate SLIs/SLOs during testing.",
            ],
        }
        for requirement in requirements:
            plan["tests"].append(
                f"Derive acceptance criteria and test cases for requirement: {requirement}"
            )
        return plan

    def respond_to_instruction(self, instruction: str) -> str:  # noqa: D401 - see base
        return (
            f"{self.name} will extend validation charters to cover instruction: {instruction}. "
            "Regression and exploratory suites will be updated accordingly."
        )


TEAM_TEMPLATE = {
    "architect": Architect(
        name="Architect",
        focus_areas=["architecture", "quality attributes"],
        responsibilities=[
            "Transform requirements into architecture decisions.",
            "Maintain ADR repository and architecture guardrails.",
        ],
    ),
    "developers": [
        Developer(
            name="Developer A",
            focus_areas=["backend", "APIs"],
            responsibilities=["Implement services", "Review peers"],
            skills=["Python", "Go"],
        ),
        Developer(
            name="Developer B",
            focus_areas=["frontend", "UX"],
            responsibilities=["Develop UI", "Maintain accessibility"],
            skills=["TypeScript", "React"],
        ),
        Developer(
            name="Developer C",
            focus_areas=["DevOps", "Tooling"],
            responsibilities=["CI/CD", "Observability"],
            skills=["Terraform", "Kubernetes"],
        ),
    ],
    "testers": [
        Tester(
            name="Tester A",
            focus_areas=["automation", "regression"],
            responsibilities=["Maintain automated suite"],
            specialties=["Selenium", "Playwright"],
        ),
        Tester(
            name="Tester B",
            focus_areas=["performance", "security"],
            responsibilities=["Performance testing", "Security validation"],
            specialties=["k6", "ZAP"],
        ),
        Tester(
            name="Tester C",
            focus_areas=["usability", "accessibility"],
            responsibilities=["UX validation", "Assist UAT"],
            specialties=["WCAG", "Manual"],
        ),
    ],
    "best_practices": BEST_PRACTICES,
}
