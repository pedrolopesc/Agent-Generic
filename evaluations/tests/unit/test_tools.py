from unittest.mock import Mock, patch

import httpx
import pytest

from sandbox.runner import CommandResult
from tools.github import github_issue
from tools.platformio import build_platformio_tool


@pytest.mark.parametrize(
    "repository,number",
    [("../repo", 1), ("a/..", 1), ("a/.", 1), ("a/b", 0), ("https://evil.test", 1)],
)
def test_github_rejects_invalid_identifiers(repository, number):
    with patch("tools.github.httpx.Client") as client:
        with pytest.raises(ValueError):
            github_issue.invoke({"repository": repository, "number": number})
        client.assert_not_called()


def test_github_returns_only_issue_fields(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "example-secret")
    response = httpx.Response(
        200,
        json={
            "title": "bug",
            "body": "details",
            "state": "open",
            "html_url": "https://github.com/a/b/issues/1",
            "internal": "discard",
        },
        request=httpx.Request("GET", "https://api.github.com"),
    )
    with patch("tools.github.httpx.Client") as client:
        client.return_value.__enter__.return_value.get.return_value = response
        result = github_issue.invoke({"repository": "a/b", "number": 1})
    assert set(result) == {"title", "body", "state", "html_url"}
    assert result["title"] == "bug"
    assert (
        client.return_value.__enter__.return_value.get.call_args.kwargs["headers"]["Authorization"]
        == "Bearer example-secret"
    )


def test_platformio_rejects_shell_injection():
    runner = Mock()
    tool = build_platformio_tool(runner)
    with pytest.raises(ValueError):
        tool.invoke({"environment": "esp32; echo unsafe"})
    runner.run.assert_not_called()


def test_platformio_runs_selected_environment():
    runner = Mock()
    runner.run.return_value = CommandResult(
        command="pio run -e esp32", exit_code=0, output="SUCCESS"
    )
    result = build_platformio_tool(runner).invoke({"environment": "esp32"})
    runner.run.assert_called_once_with("pio run -e esp32")
    assert "SUCCESS" in result
