# Evaluations

## Test categories

| Category | Directory | Scope | Required for main |
|---|---|---|---|
| Unit | `evaluations/tests/unit/` | Models, mocked runner, stopping policy, limits, tools, and commit interpretation | Yes |
| Functional | `evaluations/tests/functional/` | HTTP contracts and delivery lifecycle using the real API/graph with simulated external dependencies | Yes |
| Integration | `evaluations/tests/integration/` | Construction with the real Deep Agents library and Docker execution | No |

```powershell
python -m pytest evaluations/tests/unit -m unit
python -m pytest evaluations/tests/functional -m functional
python -m pytest evaluations/tests/integration -m integration
```

Categories are assigned automatically from the directory in `conftest.py`; markers are registered with `--strict-markers`. Default pytest discovery includes only unit and functional tests. To collect all categories explicitly, run `python -m pytest evaluations/tests`.

The Deep Agents integration does not call a model provider. The Docker test is skipped until you set `$env:RUN_DOCKER_TESTS = "1"` after building `agent-sandbox:local` and starting the daemon. Once enabled, the test fails if Docker or the image is missing. It verifies reading, shared writes, and the absence of a default network route inside the container.

See [CI and versioning](ci.md) for required checks, JUnit artifacts, and releases.

## TDD policy coverage

Unit tests check valid red/green/refactor ordering, matching red/green commands, infrastructure exit codes, incomplete cycles, and invalidation after later failures. Runner tests verify actual exit codes and retention of TDD evidence after an attempt reset. Functional tests reject model approval without TDD and verify that a cycle can continue across attempts. See [TDD workflow](tdd.md).

## Task dataset

`python -m pytest` checks retry and exhaustion routing, feedback between attempts, rejection of approval without execution, path isolation, Docker arguments, the absence of a host fallback, and API authentication and input validation. Models and subprocesses are simulated; these tests do not measure LLM quality.

`evaluations/datasets/tasks.jsonl` contains initial tasks and human-defined criteria. With the real API running, execute:

```powershell
python -m evaluations.run --token YOUR_TOKEN --url http://127.0.0.1:8000
```

The command prints per-task results and aggregate metrics: completion rate and mean iteration count. HTTP errors abort evaluation so they are not mistaken for rejected deliveries. Dataset criteria guide the prompt; they are not an independent test oracle. For rigorous model comparisons, expand the dataset, add external acceptance tests and repeated runs, and record cost and latency. Real evaluation consumes tokens and executes commands in Docker.
