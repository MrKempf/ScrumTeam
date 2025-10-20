"""Role definitions for the Scrum-based agentic AI team."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Union

from .best_practices import BEST_PRACTICES


@dataclass
class LLMProviderConfig:
    """Configuration describing which LLM backs a role."""

    provider: str
    deployment: str = "cloud"
    model: str | None = None

    def as_dict(self) -> Dict[str, str]:
        """Return a serialisable representation of the provider configuration."""

        data: Dict[str, str] = {
            "provider": self.provider,
            "deployment": self.deployment,
        }
        if self.model:
            data["model"] = self.model
        return data

    def describe(self) -> str:
        """Create a short human-friendly summary of the provider setup."""

        if self.model:
            return f"{self.provider} ({self.deployment}, model={self.model})"
        return f"{self.provider} ({self.deployment})"


LLMProviderSpec = Union["LLMProviderConfig", str, Mapping[str, Any]]


def _coerce_llm_provider(spec: LLMProviderSpec) -> LLMProviderConfig:
    """Normalise a user-supplied provider spec into an ``LLMProviderConfig``."""

    if isinstance(spec, LLMProviderConfig):
        return spec

    if isinstance(spec, str):
        provider_part, model = (spec.split(":", 1) + [None])[:2]
        provider = provider_part.strip()
        detected_model = model.strip() if model else None
        deployment = "local" if provider.lower() in {"ollama", "local"} else "cloud"
        # If the provider itself encodes both the runtime and the name (e.g. "local:ollama"),
        # prefer explicit deployment instructions.
        if provider.lower() == "local" and detected_model:
            provider, detected_model = detected_model, None
        return LLMProviderConfig(provider=provider, deployment=deployment, model=detected_model)

    if isinstance(spec, Mapping):
        data = dict(spec)
        provider_value = data.get("provider") or data.get("name")
        if not provider_value:
            raise ValueError("Provider configuration dictionaries must include a 'provider' key.")
        provider = str(provider_value)
        deployment_value = data.get("deployment") or data.get("location")
        if deployment_value is None:
            deployment = "local" if provider.lower() == "ollama" else "cloud"
        else:
            deployment = str(deployment_value)
        model_value = data.get("model")
        model = None if model_value is None else str(model_value)
        return LLMProviderConfig(provider=provider, deployment=deployment, model=model)

    raise TypeError("Unsupported provider specification. Use a string, mapping, or LLMProviderConfig instance.")


@dataclass
class Role:
    """Base class for all roles."""

    name: str
    focus_areas: List[str]
    responsibilities: List[str]
    llm_provider: LLMProviderConfig = field(
        default_factory=lambda: LLMProviderConfig(provider="openai", deployment="cloud")
    )

    def summarize(self) -> str:
        return f"{self.name}: focus on {', '.join(self.focus_areas)}"

    def respond_to_instruction(self, instruction: str) -> str:
        """Describe how the role will react to an additional instruction."""

        return f"{self.name} acknowledges instruction '{instruction}' and will incorporate it into upcoming work."

    def set_llm_provider(self, provider: LLMProviderSpec) -> None:
        """Assign a new LLM provider to the role."""

        self.llm_provider = _coerce_llm_provider(provider)


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
        llm_provider=LLMProviderConfig(provider="openai", deployment="cloud", model="gpt-4o"),
    ),
    "developers": [
        Developer(
            name="Developer A",
            focus_areas=["backend", "APIs"],
            responsibilities=["Implement services", "Review peers"],
            skills=["Python", "Go"],
            llm_provider=LLMProviderConfig(provider="openai", deployment="cloud", model="gpt-4o-mini"),
        ),
        Developer(
            name="Developer B",
            focus_areas=["frontend", "UX"],
            responsibilities=["Develop UI", "Maintain accessibility"],
            skills=["TypeScript", "React"],
            llm_provider=LLMProviderConfig(provider="openai", deployment="cloud", model="gpt-4o-mini"),
        ),
        Developer(
            name="Developer C",
            focus_areas=["DevOps", "Tooling"],
            responsibilities=["CI/CD", "Observability"],
            skills=["Terraform", "Kubernetes"],
            llm_provider=LLMProviderConfig(provider="ollama", deployment="local", model="llama3"),
        ),
    ],
    "testers": [
        Tester(
            name="Tester A",
            focus_areas=["automation", "regression"],
            responsibilities=["Maintain automated suite"],
            specialties=["Selenium", "Playwright"],
            llm_provider=LLMProviderConfig(provider="openai", deployment="cloud", model="gpt-4o-mini"),
        ),
        Tester(
            name="Tester B",
            focus_areas=["performance", "security"],
            responsibilities=["Performance testing", "Security validation"],
            specialties=["k6", "ZAP"],
            llm_provider=LLMProviderConfig(provider="ollama", deployment="local", model="llama3"),
        ),
        Tester(
            name="Tester C",
            focus_areas=["usability", "accessibility"],
            responsibilities=["UX validation", "Assist UAT"],
            specialties=["WCAG", "Manual"],
            llm_provider=LLMProviderConfig(provider="openai", deployment="cloud", model="gpt-4o-mini"),
        ),
    ],
    "best_practices": BEST_PRACTICES,
}
