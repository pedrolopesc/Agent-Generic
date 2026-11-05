import pytest
from pydantic import ValidationError

from orchestration.policies import Settings, workspace_for


def test_workspace_cannot_escape_root(tmp_path):
    with pytest.raises(ValueError):
        workspace_for(tmp_path, "../escape")
    assert workspace_for(tmp_path, "run-123").parent == tmp_path.resolve()


@pytest.mark.parametrize("limit", [0, 11])
def test_invalid_server_iteration_limit(limit):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, max_iterations=limit)
