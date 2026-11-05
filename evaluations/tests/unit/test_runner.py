import subprocess
from unittest.mock import patch

import pytest

from sandbox.runner import SandboxRunner


def test_workspace_confinement(tmp_path):
    runner = SandboxRunner(tmp_path)
    runner.write("src/main.py", "print(1)")
    assert runner.read("src/main.py") == "print(1)"
    for path in ("../outside", "/etc/passwd", "C:/Windows/file"):
        with pytest.raises(ValueError):
            runner.write(path, "unsafe")


def test_docker_isolation_and_failure(tmp_path):
    runner = SandboxRunner(tmp_path)
    with patch(
        "sandbox.runner.subprocess.run",
        return_value=subprocess.CompletedProcess([], 1, "", "failed"),
    ) as run:
        result = runner.run("pytest")
    args = run.call_args_list[0].args[0]
    assert args[:3] == ["docker", "run", "--rm"]
    assert "--network=none" in args and "--read-only" in args
    assert result.exit_code == 1
    assert runner.history == [result]


def test_no_host_fallback(tmp_path):
    runner = SandboxRunner(tmp_path)
    with patch("sandbox.runner.subprocess.run", side_effect=FileNotFoundError("docker")) as run:
        assert runner.run("echo test").exit_code == 127
        assert run.call_count == 2
        assert run.call_args.args[0][:3] == ["docker", "rm", "-f"]


def test_timeout_removes_container(tmp_path):
    runner = SandboxRunner(tmp_path)
    with patch(
        "sandbox.runner.subprocess.run",
        side_effect=[subprocess.TimeoutExpired("docker", 120), subprocess.CompletedProcess([], 0)],
    ) as run:
        assert runner.run("sleep 999").exit_code == 124
    start = run.call_args_list[0].args[0]
    cleanup = run.call_args_list[1].args[0]
    assert cleanup == ["docker", "rm", "-f", start[start.index("--name") + 1]]


def test_tdd_evidence_uses_real_exit_codes_and_survives_attempt_reset(tmp_path):
    runner = SandboxRunner(tmp_path)
    results = [
        subprocess.CompletedProcess([], code, "test output", "") for code in [1, 0, 0, 0, 0, 0]
    ]
    with patch("sandbox.runner.subprocess.run", side_effect=results):
        red = runner.run_tests("pytest -q", "red")
        runner.history.clear()
        green = runner.run_tests("pytest -q", "green")
        refactor = runner.run_tests("pytest", "refactor")
    assert red.exit_code == 1
    assert green.exit_code == refactor.exit_code == 0
    assert [result.phase for result in runner.tdd_history] == ["red", "green", "refactor"]
    assert runner.history == [green, refactor]


@pytest.mark.parametrize("command,phase", [("", "red"), ("pytest", "invalid")])
def test_invalid_tdd_request_does_not_execute(tmp_path, command, phase):
    runner = SandboxRunner(tmp_path)
    with patch.object(runner, "run") as run:
        with pytest.raises(ValueError):
            runner.run_tests(command, phase)
        run.assert_not_called()
