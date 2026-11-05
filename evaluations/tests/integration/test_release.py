import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import tomlkit


@pytest.mark.parametrize(("baseline", "expected"), [("1.2.3", "1.3.0"), (None, "1.0.0")])
def test_semantic_release_updates_version_changelog_and_tag_without_push(
    tmp_path, baseline, expected
):
    """Usa Git e PSR reais, mas somente em um repositório descartável e sem publicação."""
    source = Path(__file__).parents[3] / "pyproject.toml"
    project = tomlkit.parse(source.read_text(encoding="utf-8"))
    project["project"]["version"] = baseline or "0.1.0"
    (tmp_path / "pyproject.toml").write_text(tomlkit.dumps(project), encoding="utf-8")
    env = {**os.environ, "GH_TOKEN": "local-test-token", "GIT_CONFIG_NOSYSTEM": "1"}

    def command(*args):
        result = subprocess.run(
            args, cwd=tmp_path, env=env, text=True, capture_output=True, timeout=60
        )
        assert result.returncode == 0, result.stdout + result.stderr
        return result.stdout.strip()

    command("git", "init", "--initial-branch=main")
    command("git", "config", "user.name", "Release Test")
    command("git", "config", "user.email", "release@example.test")
    command("git", "config", "commit.gpgsign", "false")
    command("git", "config", "tag.gpgsign", "false")
    command("git", "remote", "add", "origin", "https://github.com/example/agent.git")
    command("git", "add", ".")
    command("git", "commit", "-m", "chore: baseline")
    if baseline:
        command("git", "tag", f"v{baseline}")
    (tmp_path / "feature.txt").write_text("feature", encoding="utf-8")
    command("git", "add", ".")
    command("git", "commit", "-m", "feat: add new capability")
    command(sys.executable, "-m", "semantic_release", "version", "--no-push", "--no-vcs-release")
    assert (
        tomllib.loads((tmp_path / "pyproject.toml").read_text(encoding="utf-8"))["project"][
            "version"
        ]
        == expected
    )
    assert f"v{expected}" in command("git", "tag", "--list")
    changelog = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"v{expected}" in changelog
    if baseline:
        assert "add new capability" in changelog.lower()
    assert command("git", "log", "-1", "--format=%s") == f"chore(release): {expected}"
    # Commits documentais e o próprio commit de release não iniciam um novo aumento.
    (tmp_path / "notes.md").write_text("docs", encoding="utf-8")
    command("git", "add", ".")
    command("git", "commit", "-m", "docs: describe usage")
    command(sys.executable, "-m", "semantic_release", "version", "--no-push", "--no-vcs-release")
    tags = ([f"v{baseline}"] if baseline else []) + [f"v{expected}"]
    assert command("git", "tag", "--list").splitlines() == sorted(tags)
