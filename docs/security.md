# Sandbox and operational limitations

The runner starts one container per command, with networking disabled, a read-only root filesystem, user 65534, dropped capabilities, no-new-privileges, and memory, CPU, process, and time limits. Only the run's workspace is mounted for writing; `/tmp` uses tmpfs. API credential environment variables are not forwarded to the container. On timeout, the runner explicitly attempts to remove the container using its unique name.

The Docker daemon must be running. On Linux, ensure user 65534 can write to the mounted directory; use ACLs or a user/image tailored to the environment. The runner does not automatically change host permissions. Task dependencies must be preinstalled in the image because commands have no network access.

The example binds the API to localhost, requires a Bearer token, and does not expose arbitrary execution paths. File paths are resolved and restricted to the workspace root. Do not share a workspace with untrusted processes: these checks do not eliminate symlink races or hardlinks created by malicious code. Docker with a bind mount is not a sufficient boundary for hostile multiuser execution; use ephemeral VM environments for that scenario.

The reviewer subagent can execute workspace commands and modify files through the shell, despite its review instructions. Files and external results may contain prompt injection. Prompts instruct the agent to treat them as data, but this is not an absolute guarantee.

The iteration limit is neither a financial limit nor a token budget. Each attempt may involve many calls and commands. The synchronous API does not implement quotas, client cancellation, an overall duration limit, or concurrency admission control. Command output is truncated after capture, so excessive output can still consume host memory. Before exposing a public service, implement isolated workers, quotas, durable storage, and output limits.

An approved delivery means model approval, successful execution in the current attempt, and recorded red/green/refactor evidence. Phase labels do not prove that tests were written before production code; see [TDD limitations](tdd.md). A successful command does not guarantee coverage or correctness; add deterministic validators for each task type. The task-execution agent does not deploy or publish automatically.
