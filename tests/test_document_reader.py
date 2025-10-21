from pathlib import Path

import pytest

from scrum_team.document_reader import extract_keywords, read_requirements


def test_read_requirements_strips_formatting(tmp_path: Path) -> None:
    requirement_file = tmp_path / "requirements.md"
    requirement_file.write_text(
        """
        # Requirements

        - Enable real-time insights.
        - Support mobile and web clients.

        \n\n
        * Maintain audit logs.
        """,
        encoding="utf-8",
    )

    requirements = read_requirements(requirement_file)

    assert requirements == [
        "Requirements",
        "Enable real-time insights.",
        "Support mobile and web clients.",
        "Maintain audit logs.",
    ]


@pytest.mark.parametrize(
    "requirements, expected_keywords",
    [
        (
            [
                "Enable real-time processing of sensor data",
                "Guarantee security and privacy for customers",
            ],
            [
                "customers",
                "data",
                "enable",
                "guarantee",
                "privacy",
                "processing",
                "real-time",
                "security",
                "sensor",
            ],
        ),
        (
            ["Keep UI fast", "Add AI"],
            ["fast", "keep"],
        ),
    ],
)
def test_extract_keywords(requirements, expected_keywords):
    assert extract_keywords(requirements) == expected_keywords
