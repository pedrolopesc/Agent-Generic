from hmac import compare_digest
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from agents.developer import build_developer
from models.factory import create_model
from orchestration.graph import build_graph
from orchestration.policies import Settings, workspace_for
from sandbox.runner import SandboxRunner
from tools.github import github_issue
from tools.platformio import build_platformio_tool
from tools.telemetry import timed_event

app = FastAPI(title="Agent Generic", version="0.1.0")
security = HTTPBearer(auto_error=False)


def settings():
    return Settings()


def authorize(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    config: Settings = Depends(settings),
):
    if not config.api_token:
        raise HTTPException(503, "Configure AGENT_API_TOKEN antes de executar tarefas")
    if credentials is None or not compare_digest(credentials.credentials, config.api_token):
        raise HTTPException(401, "Token inválido")


class RunRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=50_000)
    max_iterations: int = Field(default=3, ge=1, le=10)


class RunResponse(BaseModel):
    run_id: UUID
    status: str
    iteration: int
    delivery: str
    feedback: str
    evidence: list[str]
    tdd_evidence: list[str] = Field(default_factory=list)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/runs", response_model=RunResponse, dependencies=[Depends(authorize)])
def run_task(request: RunRequest, config: Settings = Depends(settings)):
    run_id = uuid4()
    workspace = workspace_for(config.workspace_root, str(run_id))
    runner = SandboxRunner(workspace)

    def model(role):
        return create_model(role, config.model_config_path)

    try:
        developer = build_developer(
            model("developer"),
            runner,
            model("reviewer"),
            [github_issue, build_platformio_tool(runner)],
        )
        graph = build_graph(model("diagnostic"), developer, model("validator"), runner)
        with timed_event("run", str(run_id)):
            state = graph.invoke(
                {
                    "prompt": request.prompt,
                    "iteration": 0,
                    "max_iterations": min(request.max_iterations, config.max_iterations),
                },
                {"configurable": {"thread_id": str(run_id)}, "recursion_limit": 100},
            )
    except Exception as exc:
        # Logs podem conter detalhes internos; a resposta não expõe credenciais nem prompts.
        import logging

        logging.getLogger("agent.api").exception("run_failed run_id=%s", run_id)
        raise HTTPException(502, f"Falha na execução {run_id}; consulte os logs") from exc
    return RunResponse(
        run_id=run_id,
        **{
            key: state[key]
            for key in ("status", "iteration", "delivery", "feedback", "evidence", "tdd_evidence")
        },
    )
