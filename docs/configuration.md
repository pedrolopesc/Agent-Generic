# Configuration

`models/config.yaml` defines `default` settings and overrides under `roles`: `diagnostic`, `developer`, `reviewer`, and `validator`. The factory uses `langchain.chat_models.init_chat_model`; the graph does not hardcode a provider client import.

```yaml
default:
  provider: openai
  model: gpt-4.1
  temperature: 0
roles:
  validator:
    provider: anthropic
    model: claude-sonnet-4-5
```

These names are examples and depend on the provider's catalog and your access. For Anthropic, install `pip install -e ".[anthropic]"` and set `ANTHROPIC_API_KEY`. For Ollama, install `pip install -e ".[ollama]"`, use `provider: ollama`, and select an installed model that supports tool calling and structured output. Models that do not accept `temperature` require a factory adjustment.

Variables read from `.env` or the environment:

| Variable | Default | Purpose |
|---|---|---|
| AGENT_API_TOKEN | Empty | Required for POST /runs |
| AGENT_WORKSPACE_ROOT | ./workspaces | Root directory for generated files |
| AGENT_MAX_ITERATIONS | 3 | Server limit, from 1 to 10 |
| AGENT_MODEL_CONFIG_PATH | Packaged configuration | Alternative YAML file |
| OPENAI_API_KEY | No default | OpenAI credential |
| GITHUB_TOKEN | Optional | Read private issues |

The API uses the smaller of the request limit and the server limit. Each request creates a UUID and an empty workspace. Models are constructed at request time, so configuration changes apply to the next run.
