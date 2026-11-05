import re

import httpx
from langchain_core.tools import tool


def build_gcp_tool():
    @tool
    def gcp_project(project_id: str) -> dict:
        """Consulte metadados de um projeto GCP usando Application Default Credentials."""
        import google.auth
        from google.auth.transport.requests import Request

        if not re.fullmatch(r"[a-z][a-z0-9-]{4,28}[a-z0-9]", project_id):
            raise ValueError("ID de projeto inválido")
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform.read-only"]
        )
        credentials.refresh(Request())
        response = httpx.get(
            f"https://cloudresourcemanager.googleapis.com/v3/projects/{project_id}",
            headers={"Authorization": f"Bearer {credentials.token}"},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    return gcp_project
