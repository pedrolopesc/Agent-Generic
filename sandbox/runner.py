import subprocess
from pathlib import Path
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel


class CommandResult(BaseModel):
    command: str
    exit_code: int
    output: str
    phase: Literal["command", "red", "green", "refactor"] = "command"


class SandboxRunner:
    """Comandos somente via Docker; não há fallback para execução no host."""

    def __init__(self, workspace: Path, image: str = "agent-sandbox:local", timeout: int = 120):
        self.workspace = workspace.resolve()
        self.image = image
        self.timeout = timeout
        self.history: list[CommandResult] = []
        self.tdd_history: list[CommandResult] = []

    def _path(self, relative: str) -> Path:
        path = Path(relative)
        if path.is_absolute() or not relative or ":" in relative:
            raise ValueError("Use um caminho relativo ao workspace")
        target = (self.workspace / path).resolve()
        if target == self.workspace or self.workspace not in target.parents:
            raise ValueError("Caminho fora do workspace")
        return target

    def read(self, path: str) -> str:
        return self._path(path).read_text(encoding="utf-8")[:100_000]

    def write(self, path: str, content: str):
        target = self._path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def run_tests(self, command: str, phase: Literal["red", "green", "refactor"]) -> CommandResult:
        if phase not in {"red", "green", "refactor"} or not command.strip():
            raise ValueError("A nonempty test command and valid TDD phase are required")
        result = self.run(command)
        result.phase = phase
        self.tdd_history.append(result)
        return result

    def run(self, command: str) -> CommandResult:
        container_name = f"agent-{uuid4().hex}"
        args = [
            "docker",
            "run",
            "--rm",
            "--name",
            container_name,
            "--network=none",
            "--read-only",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
            "--pids-limit=128",
            "--memory=512m",
            "--cpus=1",
            "--user=65534:65534",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--mount",
            f"type=bind,source={self.workspace},target=/workspace",
            "-w",
            "/workspace",
            self.image,
            "sh",
            "-lc",
            command,
        ]
        try:
            completed = subprocess.run(
                args, capture_output=True, text=True, timeout=self.timeout, check=False
            )
            result = CommandResult(
                command=command,
                exit_code=completed.returncode,
                output=(completed.stdout + completed.stderr)[-20_000:],
            )
        except subprocess.TimeoutExpired:
            result = CommandResult(command=command, exit_code=124, output="Tempo limite excedido")
        except OSError as exc:
            result = CommandResult(command=command, exit_code=127, output=str(exc))
        finally:
            # O timeout do cliente Docker não encerra necessariamente o container.
            try:
                subprocess.run(
                    ["docker", "rm", "-f", container_name],
                    capture_output=True,
                    timeout=10,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                pass
        self.history.append(result)
        return result
