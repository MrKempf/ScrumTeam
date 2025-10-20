"""Curated list of modern software development best practices."""

from __future__ import annotations

BEST_PRACTICES = {
    "architecture": [
        "Document architecture decisions through Architecture Decision Records (ADRs).",
        "Design for scalability and resilience using modular components and clear interfaces.",
        "Prioritize security and privacy from the architecture phase onward.",
    ],
    "development": [
        "Adopt trunk-based development with short-lived feature branches.",
        "Mandate peer code reviews before merging any change.",
        "Automate builds, dependency scanning, and static analysis.",
        "Favor clean code principles, SOLID design, and idiomatic language constructs.",
    ],
    "testing": [
        "Automate unit, integration, and end-to-end tests with clear ownership.",
        "Maintain high coverage on critical paths and verify non-functional requirements.",
        "Incorporate test data management and observability-driven validation.",
    ],
    "process": [
        "Use sprint reviews, retrospectives, and daily stand-ups to inspect and adapt.",
        "Track work through transparent Kanban or sprint boards with clear Definition of Done.",
        "Integrate continuous deployment practices with feature flags and staged rollouts.",
    ],
}


def all_best_practices() -> list[str]:
    """Return a flattened list of all best practices."""
    aggregated: list[str] = []
    for section in BEST_PRACTICES.values():
        aggregated.extend(section)
    return aggregated
