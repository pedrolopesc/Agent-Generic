from unittest.mock import patch

from models.factory import create_model


def test_role_override(tmp_path):
    config = tmp_path / "models.yaml"
    config.write_text(
        "default:\n  provider: openai\n  model: base\n  temperature: 0\nroles:\n  validator:\n    model: reviewer\n",
        encoding="utf-8",
    )
    with patch("models.factory.init_chat_model") as factory:
        create_model("validator", config)
    factory.assert_called_once_with("reviewer", model_provider="openai", temperature=0)
