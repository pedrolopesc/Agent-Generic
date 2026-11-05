# Agent Generic

[![Tests](https://github.com/pedrolopesc/Agent-Generic/actions/workflows/tests.yml/badge.svg?branch=main&event=push)](https://github.com/pedrolopesc/Agent-Generic/actions/workflows/tests.yml)

A prompt-driven development agent: LangGraph controls diagnosis, development, validation, and retries; LangChain lets you switch models; Deep Agents provides planning, virtual filesystem tools, and delegation to a reviewer subagent.

This is an initial implementation inspired by coding agent workflows. The API accepts a task and produces files in a workspace isolated by run, command execution evidence, and an assessment of the delivery.

## Test-Driven Development

The agent follows **Red → Green → Refactor**: write a behavioral test first and observe its expected failure, implement the smallest change to pass the same test, then refactor and run regression tests. The diagnostic model plans this cycle, the developer records real runs with `tdd_run_tests`, and validation rejects deliveries without an ordered red/green/refactor cycle, even when the model approves.

TDD evidence persists across attempts within a run and is returned in `tdd_evidence`. This checks execution order and outcomes; it does not prove edit order or test quality. The current gate has no automatic non-code exemption. See [TDD workflow and enforcement](docs/tdd.md) for tool examples, acceptance rules, and limitations.

## Requirements

- Python 3.11 or later.
- A running Docker Engine or Docker Desktop with Linux containers.
- An LLM provider API key for a model that supports tool calling and structured output.

## Installation (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY` and your own `AGENT_API_TOKEN`. `.env` is excluded from version control. Set the model name in `models/config.yaml` according to your account's access.

```powershell
docker build -t agent-sandbox:local -f sandbox/Dockerfile .
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
$headers = @{ Authorization = "Bearer YOUR_TOKEN" }
$body = @{
  prompt = "Use TDD to create calculator.py with add(a, b): write and run a failing pytest test first, implement the function, then refactor and run the regression suite."
  max_iterations = 3
} | ConvertTo-Json
$result = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/runs -Headers $headers -ContentType "application/json" -Body $body
$result | ConvertTo-Json -Depth 8
```

Files are stored in `workspaces/<run_id>/`. The request is synchronous and may take several minutes. Interactive API documentation is available in [Swagger UI](http://127.0.0.1:8000/docs). `GET /health` checks the process; it does not check Docker or credentials.

The response includes `status` (`completed` or `exhausted`), `iteration`, `delivery`, `feedback`, `evidence`, and `tdd_evidence`. `exhausted` means the delivery was not approved within the attempt limit. Infrastructure or model errors return HTTP 502 with an identifier for looking up logs.

## Project structure

```text
agents/         diagnostic.py, developer.py, monitor.py, validator.py
orchestration/  graph.py, state.py, policies.py
tools/          github.py, gcp.py, platformio.py, telemetry.py
models/         factory.py, config.yaml
sandbox/        Dockerfile, runner.py
evaluations/    datasets/, metrics.py, run.py, tests/
api/            main.py
docs/           architecture, configuration, integrations, security, and evaluation
```

## Verification

```powershell
python -m pytest evaluations/tests/unit -m unit
python -m pytest evaluations/tests/functional -m functional
# Integration tests (excluded from required main checks):
python -m pytest evaluations/tests/integration -m integration
python -m ruff check .
python -m evaluations.run --token YOUR_TOKEN
```

The `unit` and `functional` tests require neither API keys nor Docker: they use model and subprocess test doubles. `python -m pytest` runs these two categories by default. Run `integration` tests explicitly; the Docker test requires `RUN_DOCKER_TESTS=1` and a prepared image. Dataset evaluation calls the real API, requires Docker and credentials, and consumes tokens.

## Documentation

- [Architecture and execution lifecycle](docs/architecture.md)
- [TDD workflow and enforcement](docs/tdd.md)
- [Models and configuration](docs/configuration.md)
- [Tools and extensions](docs/integrations.md)
- [Sandbox, permissions, and limitations](docs/security.md)
- [Evaluations and metrics](docs/evaluations.md)
- [Libraries and references](docs/dependencies.md)
- [CI, versioning, and main branch protection](docs/ci.md)

Current limitations: workspaces start empty; there is no automatic repository import, streaming, chat interface, job queue, or resumption after restart. Checkpoints are in memory and scoped to the request. Validation uses real evidence and a model, but does not prove correctness. Read the documentation before using the project as a shared service.

## Automatic versioning

The `Tests` workflow runs only **Unit tests** and **Functional tests** for PRs targeting `main` and pushes to `main`. After a successful push check, `Release` uses Conventional Commits to generate the version, `CHANGELOG.md`, tag, and GitHub Release: `fix`/`perf` trigger a patch bump, `feat` triggers a minor bump, and `!` or `BREAKING CHANGE:` triggers a major bump. Standalone `docs`, `test`, `ci`, and `chore` commits do not create a version. With no existing tags, the first release is `1.0.0`.

The badge displays the actual workflow result on `main`; it has no result until the first GitHub run. To prevent merges with failing tests, configure required checks as described in [docs/ci.md](docs/ci.md).
