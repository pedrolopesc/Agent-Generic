from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGENT_", env_file=".env", extra="ignore")
    workspace_root: Path = Path("workspaces")
    api_token: str = ""
    max_iterations: int = Field(default=3, ge=1, le=10)
    model_config_path: str | None = None


def workspace_for(root: Path, run_id: str) -> Path:
    root = root.resolve()
    target = (root / run_id).resolve()
    if target.parent != root:
        raise ValueError("Workspace fora da raiz permitida")
    target.mkdir(parents=True, exist_ok=True)
    return target
