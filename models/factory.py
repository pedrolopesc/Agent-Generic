from pathlib import Path

import yaml
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, ConfigDict, Field


class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: str
    model: str
    temperature: float = Field(default=0, ge=0, le=2)


def create_model(role: str = "developer", config_path: str | Path | None = None):
    load_dotenv(override=False)
    path = Path(config_path) if config_path else Path(__file__).with_name("config.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    config = ModelConfig.model_validate({**data["default"], **data.get("roles", {}).get(role, {})})
    return init_chat_model(
        config.model, model_provider=config.provider, temperature=config.temperature
    )
