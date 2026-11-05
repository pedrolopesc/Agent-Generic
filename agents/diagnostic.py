SYSTEM_PROMPT = """Analyze the task and identify requirements, risks, and verifiable acceptance
criteria. Build a TDD plan: identify behavioral tests to write first, the expected red failure,
the smallest implementation needed for green, and the regression suite to run after refactoring.
For bugs, identify an existing or new regression test that reproduces the defect. Distinguish
behavioral test failures from environment/setup failures. Do not claim to have executed actions.
Provide a concise diagnosis and plan."""


def diagnose(model, prompt: str) -> str:
    return str(model.invoke([("system", SYSTEM_PROMPT), ("human", prompt)]).content)
