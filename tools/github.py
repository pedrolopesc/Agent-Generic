import os
import re

import httpx
from langchain_core.tools import tool


@tool
def github_issue(repository: str, number: int) -> dict:
    """Consulte uma issue do GitHub. repository deve ser owner/repo."""
    if (
        not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
        or any(part in {".", ".."} for part in repository.split("/"))
        or number < 1
    ):
        raise ValueError("Repositório ou número inválido")
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    with httpx.Client(timeout=20) as client:
        response = client.get(
            f"https://api.github.com/repos/{repository}/issues/{number}", headers=headers
        )
        response.raise_for_status()
        issue = response.json()
        return {key: issue.get(key) for key in ("title", "body", "state", "html_url")}
