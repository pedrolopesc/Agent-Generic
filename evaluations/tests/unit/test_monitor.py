import pytest

from agents.monitor import monitor


@pytest.mark.parametrize(
    ("approved", "iteration", "limit", "expected"),
    [
        (True, 1, 3, "completed"),
        (True, 3, 3, "completed"),
        (False, 1, 3, "retrying"),
        (False, 3, 3, "exhausted"),
    ],
)
def test_stop_policy(approved, iteration, limit, expected):
    assert monitor({"approved": approved, "iteration": iteration, "max_iterations": limit}) == {
        "status": expected
    }
