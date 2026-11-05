from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from api.main import app, settings
from orchestration.policies import Settings
from orchestration.state import Verdict
from sandbox.runner import CommandResult


def test_prompt_to_validated_workspace_delivery(tmp_path):
    """API e grafo reais; apenas os modelos e a execução externa são simulados."""
    diagnostic = Mock()
    diagnostic.invoke.return_value = SimpleNamespace(content="Criar answer.py e verificar saída 42")
    validator = Mock()
    validator.with_structured_output.return_value.invoke.return_value = Verdict(
        approved=True, feedback="Critérios atendidos"
    )

    def developer_factory(model, runner, *args):
        def invoke(*args, **kwargs):
            runner.write("answer.py", "print(42)\n")
            for phase, code in [("red", 1), ("green", 0), ("refactor", 0)]:
                result = CommandResult(
                    command="pytest -q", exit_code=code, output="42", phase=phase
                )
                runner.history.append(result)
                runner.tdd_history.append(result)
            return {"messages": [SimpleNamespace(content="answer.py criado e verificado")]}

        return SimpleNamespace(invoke=invoke)

    app.dependency_overrides[settings] = lambda: Settings(
        _env_file=None, api_token="secret", workspace_root=tmp_path
    )
    try:
        with (
            patch(
                "api.main.create_model",
                side_effect=lambda role, path: validator if role == "validator" else diagnostic,
            ),
            patch("api.main.build_developer", side_effect=developer_factory),
        ):
            response = TestClient(app).post(
                "/runs",
                headers={"Authorization": "Bearer secret"},
                json={"prompt": "Crie um programa que imprima 42 e verifique a saída"},
            )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "completed"
        assert body["iteration"] == 1
        assert (tmp_path / body["run_id"] / "answer.py").read_text() == "print(42)\n"
        assert "pytest -q" in body["evidence"][0]
        assert len(body["tdd_evidence"]) == 3
        assert "42" in validator.with_structured_output.return_value.invoke.call_args.args[0][-1][1]
    finally:
        app.dependency_overrides.clear()
