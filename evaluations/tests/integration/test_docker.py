import os

import pytest

from sandbox.runner import SandboxRunner


@pytest.mark.skipif(
    os.getenv("RUN_DOCKER_TESTS") != "1",
    reason="Defina RUN_DOCKER_TESTS=1 com Docker e imagem prontos",
)
def test_real_container_workspace_and_no_network(tmp_path):
    # Diretório criado pelo teste; permite escrita pelo UID não privilegiado da imagem no Linux.
    tmp_path.chmod(0o777)
    runner = SandboxRunner(tmp_path)
    runner.write("input.txt", "integration")
    command = (
        'python -c "from pathlib import Path; '
        "assert Path('input.txt').read_text() == 'integration'; "
        "assert '00000000' not in Path('/proc/net/route').read_text(); "
        "Path('output.txt').write_text('ok')\""
    )
    result = runner.run(command)
    assert result.exit_code == 0, result.output
    assert runner.read("output.txt") == "ok"
