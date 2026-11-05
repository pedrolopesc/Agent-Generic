from typing import TypedDict

from pydantic import BaseModel, Field


class Verdict(BaseModel):
    approved: bool
    feedback: str
    evidence: list[str] = Field(default_factory=list)


class AgentState(TypedDict, total=False):
    prompt: str
    diagnosis: str
    delivery: str
    feedback: str
    evidence: list[str]
    tdd_evidence: list[str]
    iteration: int
    max_iterations: int
    approved: bool
    status: str
