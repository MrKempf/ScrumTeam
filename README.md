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

## Features

- Architecture decisions tailored to requirement keywords with ADR guidance.
- Implementation plans for each developer with embedded peer-review steps.
- Test strategies for each tester covering automation, performance, security, and UX.
- Comprehensive checklist of contemporary software engineering best practices.
- Quality assurance guardrails ensuring all generated work is reviewed and tested.
- Full interaction log of every prompt and response so outputs remain auditable.
- Follow-up handling so product owners can steer subsequent sprints via prompts.
