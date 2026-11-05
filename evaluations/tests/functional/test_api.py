from fastapi.testclient import TestClient

from api.main import app, settings
from orchestration.policies import Settings


def test_authentication():
    app.dependency_overrides[settings] = lambda: Settings(api_token="test-secret")
    try:
        client = TestClient(app)
        assert client.get("/health").status_code == 200
        assert client.post("/runs", json={"prompt": "x"}).status_code == 401
        assert (
            client.post(
                "/runs",
                headers={"Authorization": "Bearer test-secret"},
                json={"prompt": "x", "max_iterations": 0},
            ).status_code
            == 422
        )
    finally:
        app.dependency_overrides.clear()


def test_run_response_and_server_iteration_limit(tmp_path):
    from unittest.mock import Mock, patch

    app.dependency_overrides[settings] = lambda: Settings(
        api_token="secret", workspace_root=tmp_path, max_iterations=2
    )
    graph = Mock()
    graph.invoke.return_value = {
        "status": "completed",
        "iteration": 1,
        "delivery": "done",
        "feedback": "ok",
        "evidence": ["pytest passed"],
        "tdd_evidence": [],
    }
    try:
        with (
            patch("api.main.create_model"),
            patch("api.main.build_developer"),
            patch("api.main.build_graph", return_value=graph),
        ):
            response = TestClient(app).post(
                "/runs",
                headers={"Authorization": "Bearer secret"},
                json={"prompt": "task", "max_iterations": 8},
            )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        assert graph.invoke.call_args.args[0]["max_iterations"] == 2
        assert (tmp_path / response.json()["run_id"]).is_dir()
    finally:
        app.dependency_overrides.clear()
