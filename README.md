# Agentic Scrum Team

This project implements an agentic AI that simulates a full Scrum team comprising an
architect, three developers, and three testers. The team reads requirements from an
external document, produces architecture decisions, creates implementation and testing
plans, and reinforces modern software development best practices such as mandatory code
reviews and automated testing.

## Getting Started

1. Create a requirement document (Markdown or text) where each line represents a
   requirement or constraint. You can use `docs/sample_requirements.md` as a template.
2. Run the Scrum team simulation:

   ```bash
   python main.py docs/sample_requirements.md
   ```

   Provide one or more post-sprint instructions with `--follow-up` to let the virtual
   team react to additional guidance:

   ```bash
   python main.py docs/sample_requirements.md \
     --follow-up "Prioritise accessibility across all deliverables" \
     --follow-up "Plan rollout strategy for beta customers"
   ```

   To obtain structured JSON output, append `--json`:

   ```bash
   python main.py docs/sample_requirements.md --json
   ```

## Configuring LLM Providers

Each role in the virtual team can run against a different LLM provider, whether hosted
in the cloud or locally via Ollama. Configure providers after creating the team:

```python
from scrum_team import ScrumTeam

team = ScrumTeam.default()
team.configure_llm_providers(
    {
        "architect": "openai:gpt-4o",          # Cloud model
        "developers": [
            "openai:gpt-4o-mini",                # Shared cloud configuration
            {"provider": "ollama", "model": "llama3"},  # Local Ollama model
            "ollama:llama3",                     # String shortcut for Ollama
        ],
        "testers": "ollama:llama3",             # Apply to every tester
    }
)
```

Strings follow the ``provider[:model]`` format. When the provider name is ``ollama`` the
team automatically treats it as a local deployment. Dictionaries can be used for more
explicit control by specifying ``provider``, ``model``, and optionally ``deployment``.

## Features

- Architecture decisions tailored to requirement keywords with ADR guidance.
- Implementation plans for each developer with embedded peer-review steps.
- Source code scaffolds and paired unit tests aligned with the agreed architecture decisions.
- Test strategies, executable scripts, and risk-oriented summaries for every tester.
- Comprehensive checklist of contemporary software engineering best practices.
- Quality assurance guardrails ensuring all generated work is reviewed and tested.
- Full interaction log of every prompt and response so outputs remain auditable.
- Follow-up handling so product owners can steer subsequent sprints via prompts.

## Sprint Outputs

The simulated sprint produces a complete engineering package suitable for downstream
automation:

- **ADR Decisions** – Architecture decision records captured alongside rationale and
  consequences to support traceability.
- **Source Code** – Role-specific module scaffolds reflecting the approved design and
  serving as a starting point for implementation.
- **Unit Tests** – Parametrised tests linked to each requirement to enforce coverage
  expectations from day one.
- **Test Plans** – Strategy documents covering functional and non-functional
  validations, generated per tester specialty.
- **Test Scripts** – Executable step-by-step instructions referencing required tools
  and environments.
- **Test Summaries** – Condensed reporting of anticipated coverage, risks, and next
  actions for quality stakeholders.
