from collections.abc import Sequence

from sandbox.runner import CommandResult


def assess_tdd(history: Sequence[CommandResult]) -> tuple[bool, str]:
    """Require an ordered cycle backed by actual test command results."""
    stage = "red"
    red_command = ""
    for result in history:
        if result.phase == "command":
            continue
        if result.phase == "red":
            stage = "green" if result.exit_code == 1 else "red"
            red_command = result.command.strip() if result.exit_code == 1 else ""
        elif result.phase == "green":
            if (
                stage in {"green", "refactor", "complete"}
                and result.exit_code == 0
                and result.command.strip() == red_command
            ):
                stage = "refactor"
            else:
                stage = "red"
        elif result.phase == "refactor":
            stage = (
                "complete" if stage in {"refactor", "complete"} and result.exit_code == 0 else "red"
            )
    if stage == "complete":
        return True, "TDD cycle verified: red, green, refactor."
    return False, (
        "TDD evidence incomplete: use tdd_run_tests to record a red test run (exit 1), "
        "a green run of the same command (exit 0), and a passing refactor/regression run "
        "in that order. Infrastructure errors do not establish red."
    )
