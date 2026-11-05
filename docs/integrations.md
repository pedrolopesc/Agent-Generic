# Tools and extensions

## Workspace and commands

`workspace_read` and `workspace_write` operate on paths relative to the real workspace. Deep Agents' native filesystem tools use virtual state for drafts and planning. `sandbox_run` executes commands in Docker at `/workspace` and records evidence. There is no host shell fallback. `tdd_run_tests(command, phase)` runs tests through the same runner and records `red`, `green`, or `refactor` evidence for the delivery gate. Normal shell commands alone do not satisfy TDD. See [TDD workflow](tdd.md).

## GitHub

`github_issue(repository, number)` queries the issues REST API and returns the title, body, state, and URL. It is registered in the API by default. `GITHUB_TOKEN` is optional for public content. This version has no tools for creating PRs, pushing commits, or publishing.

## GCP

`tools/gcp.py` provides `build_gcp_tool`, which queries project metadata using Resource Manager and Application Default Credentials. It is opt-in and is not registered by the default API. Install `pip install -e ".[gcp]"`, configure ADC with `gcloud auth application-default login`, and add `build_gcp_tool()` to the integrations list in `api/main.py`. Use an identity with minimal read permissions. Deployment and arbitrary gcloud commands are not supported.

## PlatformIO

`platformio_build` runs `pio run` with an optional, validated environment name. The image includes PlatformIO, but the container has no network access. Prepare an image with the project's toolchains, platforms, and dependencies already installed and accessible to user 65534. Adjust the runner image when extending the supported domain. The tool does not upload to hardware.

## Telemetry

The monitor uses logging for status and iteration updates, and `timed_event` measures duration. Configure handlers through Uvicorn or the application. LangSmith is a transitive dependency; the project does not enable external tracing. If you enable tracing through the environment, review the data being sent, including prompts, files, and tool calls.

## New tools

Create typed functions with `@tool`, document their inputs, validate paths and identifiers, and pass the tool to `build_developer`. Tools execute in the API process, so operations with external effects need explicit policies. Tools should not accept arbitrary URLs with credentials or execute a host shell.
