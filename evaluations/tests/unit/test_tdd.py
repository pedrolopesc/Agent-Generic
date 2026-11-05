import pytest

from orchestration.tdd import assess_tdd
from sandbox.runner import CommandResult


def execution(phase, code, command="pytest -q"):
    return CommandResult(command=command, exit_code=code, output="test result", phase=phase)


@pytest.mark.parametrize(
    "history",
    [
        [],
        [execution("green", 0)],
        [execution("red", 0), execution("green", 0), execution("refactor", 0)],
        [execution("red", 2), execution("green", 0), execution("refactor", 0)],
        [execution("red", 124), execution("green", 0), execution("refactor", 0)],
        [execution("red", 1), execution("green", 0, "echo success"), execution("refactor", 0)],
        [execution("red", 1), execution("refactor", 0), execution("green", 0)],
        [execution("red", 1), execution("green", 0), execution("refactor", 1)],
        [
            execution("red", 1),
            execution("green", 0),
            execution("refactor", 0),
            execution("green", 1),
        ],
    ],
)
def test_rejects_missing_invalid_or_stale_tdd_evidence(history):
    assert assess_tdd(history)[0] is False


def test_accepts_red_green_refactor_with_broader_regression_suite():
    history = [execution("red", 1), execution("green", 0), execution("refactor", 0, "pytest")]
    assert assess_tdd(history) == (True, "TDD cycle verified: red, green, refactor.")


def test_new_red_invalidates_a_previous_completed_cycle():
    history = [
        execution("red", 1),
        execution("green", 0),
        execution("refactor", 0),
        execution("red", 1),
    ]
    assert assess_tdd(history)[0] is False
