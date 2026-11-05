# Libraries and references

| Library | Purpose |
|---|---|
| LangGraph | Explicit state, conditional transitions, and checkpoints |
| LangChain | Model factory, messages, tools, and structured output |
| Deep Agents | Harness with planning, delegation, and context management |
| FastAPI / Uvicorn | Typed API, OpenAPI, and ASGI server |
| Pydantic / pydantic-settings | Input/output contracts and environment-based configuration |
| PyYAML | Editable model configuration by role |
| HTTPX | HTTP calls with timeouts for integrations |
| google-auth (optional) | ADC credentials for GCP queries |
| pytest / Ruff (development) | Tests and static checks |
| Python Semantic Release (development and CI) | Interpret Conventional Commits and automate versions, changelogs, and GitHub Releases |
| PlatformIO (image) | Compile embedded projects |

Dependencies declared in `pyproject.toml` use version ranges. When present, `requirements.lock.txt` records the validated environment with exact versions. To reproduce it, run `pip install -r requirements.lock.txt` followed by `pip install -e . --no-deps`. The lock was generated on Windows/Python 3.11 and may need adjustments for other systems.

Official references used in the design:

- [Deep Agents: create_deep_agent](https://reference.langchain.com/python/deepagents/graph/create_deep_agent)
- [Deep Agents architecture](https://github.com/langchain-ai/deepagents/blob/main/libs/ARCHITECTURE.md)
- [LangGraph: conditional transitions](https://reference.langchain.com/python/langgraph/graph/state/StateGraph/add_conditional_edges)
- [LangGraph: in-memory checkpoints](https://reference.langchain.com/python/langgraph.checkpoint/memory/InMemorySaver)

Contracts are also checked against the installed packages in the tests. No integration uses internal Codex services.
