from types import SimpleNamespace
from unittest.mock import Mock

from orchestration.graph import build_graph
from orchestration.state import Verdict
from sandbox.runner import CommandResult


def execute(tmp_path, verdicts, limit=3, evidence=True, tdd=True):
    diagnostic = Mock()
    diagnostic.invoke.return_value = SimpleNamespace(content="critérios")
    developer = Mock()
    developer.invoke.return_value = {"messages": [SimpleNamespace(content="entrega")]}
    validator = Mock()
    validator.with_structured_output.return_value.invoke.side_effect = verdicts
    runner = SimpleNamespace(
        history=[CommandResult(command="pytest", exit_code=0, output="passed")] if evidence else [],
        tdd_history=[],
    )

    def deliver(*args, **kwargs):
        if tdd:
            runner.tdd_history.extend(
                [
                    CommandResult(
                        command="pytest", exit_code=code, output="test result", phase=phase
                    )
                    for phase, code in [("red", 1), ("green", 0), ("refactor", 0)]
                ]
            )
        if evidence:
            runner.history.append(CommandResult(command="pytest", exit_code=0, output="passed"))
        return {"messages": [SimpleNamespace(content="entrega")]}

    developer.invoke.side_effect = deliver
    graph = build_graph(diagnostic, developer, validator, runner)
    result = graph.invoke(
        {"prompt": "tarefa", "iteration": 0, "max_iterations": limit},
        {"configurable": {"thread_id": "test"}},
    )
    return result, developer


def test_retry_then_success(tmp_path):
    result, developer = execute(
        tmp_path,
        [Verdict(approved=False, feedback="corrija"), Verdict(approved=True, feedback="ok")],
    )
    assert result["status"] == "completed"
    assert result["iteration"] == 2
    assert "corrija" in developer.invoke.call_args.args[0]["messages"][0][1]


def test_exhaustion(tmp_path):
    result, _ = execute(tmp_path, [Verdict(approved=False, feedback="falhou")] * 2, limit=2)
    assert result["status"] == "exhausted"
    assert result["iteration"] == 2


def test_model_cannot_approve_without_execution(tmp_path):
    result, _ = execute(tmp_path, [Verdict(approved=True, feedback="ok")], limit=1, evidence=False)
    assert result["status"] == "exhausted"


def test_model_cannot_approve_without_tdd_cycle(tmp_path):
    result, _ = execute(tmp_path, [Verdict(approved=True, feedback="ok")], limit=1, tdd=False)
    assert result["status"] == "exhausted"
    assert "TDD evidence incomplete" in result["feedback"]


def test_tdd_cycle_can_continue_across_attempts(tmp_path):
    runner = SimpleNamespace(history=[], tdd_history=[])
    diagnostic = Mock()
    diagnostic.invoke.return_value = SimpleNamespace(content="test first")
    validator = Mock()
    validator.with_structured_output.return_value.invoke.return_value = Verdict(
        approved=True, feedback="ok"
    )
    attempts = iter([[("red", 1)], [("green", 0), ("refactor", 0)]])

    def deliver(*args, **kwargs):
        for phase, code in next(attempts):
            result = CommandResult(command="pytest", exit_code=code, output="tests", phase=phase)
            runner.history.append(result)
            runner.tdd_history.append(result)
        return {"messages": [SimpleNamespace(content="delivery")]}

    graph = build_graph(diagnostic, SimpleNamespace(invoke=deliver), validator, runner)
    state = graph.invoke(
        {"prompt": "feature", "iteration": 0, "max_iterations": 2},
        {"configurable": {"thread_id": "tdd-retry"}},
    )
    assert state["status"] == "completed"
    assert state["iteration"] == 2
    assert len(state["tdd_evidence"]) == 3
    assert len(state["evidence"]) == 2
