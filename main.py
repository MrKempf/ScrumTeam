"""Command line interface for the agentic Scrum team."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scrum_team.team import ScrumTeam, summarize_iteration


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the agentic Scrum team on a requirement file.")
    parser.add_argument(
        "requirements",
        type=Path,
        help="Path to the external requirement document (Markdown or text).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of the human-readable summary.",
    )
    parser.add_argument(
        "--follow-up",
        action="append",
        default=[],
        metavar="INSTRUCTION",
        help="Provide follow-up instructions after the initial sprint output (can be repeated).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    team = ScrumTeam.default()
    result = team.run_iteration(args.requirements)

    for instruction in args.follow_up:
        team.handle_follow_up(result, instruction)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(summarize_iteration(result))


if __name__ == "__main__":
    main()
