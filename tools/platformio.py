import re

from langchain_core.tools import tool


def build_platformio_tool(runner):
    @tool
    def platformio_build(environment: str = "") -> str:
        """Compile o projeto PlatformIO presente no workspace, sem fazer upload para hardware."""
        if environment and not re.fullmatch(r"[A-Za-z0-9_-]+", environment):
            raise ValueError("Ambiente inválido")
        command = "pio run" + (f" -e {environment}" if environment else "")
        return runner.run(command).model_dump_json()

    return platformio_build
