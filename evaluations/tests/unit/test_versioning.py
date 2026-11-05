import tomllib
from pathlib import Path

import pytest
from semantic_release.cli.config import RawConfig
from semantic_release.commit_parser.conventional import ConventionalCommitParser
from semantic_release.enums import LevelBump


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("fix(api): corrige autenticação", LevelBump.PATCH),
        ("perf: reduz latência", LevelBump.PATCH),
        ("feat: adiciona servidor MCP", LevelBump.MINOR),
        ("feat(api)!: altera contrato", LevelBump.MAJOR),
        ("fix: muda contrato\n\nBREAKING CHANGE: remove campo legado", LevelBump.MAJOR),
        ("docs: explica instalação", LevelBump.NO_RELEASE),
        ("chore(release): 1.2.3", LevelBump.NO_RELEASE),
    ],
)
def test_conventional_commit_release_level(message, expected):
    config = tomllib.loads(
        (Path(__file__).parents[3] / "pyproject.toml").read_text(encoding="utf-8")
    )["tool"]["semantic_release"]
    validated = RawConfig.model_validate(config)
    assert validated.commit_parser == "conventional"
    parsed = ConventionalCommitParser().parse_message(message)
    assert parsed is not None
    assert parsed.bump == expected


def test_nonconventional_message_does_not_trigger_release():
    assert ConventionalCommitParser().parse_message("update stuff") is None
