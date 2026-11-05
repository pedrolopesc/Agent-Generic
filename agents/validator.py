from orchestration.state import Verdict


def validate(model, prompt: str, diagnosis: str, delivery: str, evidence: str) -> Verdict:
    return model.with_structured_output(Verdict).invoke(
        [
            (
                "system",
                "Validate the delivery against acceptance criteria and TDD. Approve only with "
                "actual red, green, and refactor execution evidence. Check red fails for the "
                "intended missing behavior rather than setup errors, green reruns the same "
                "test command successfully, and refactor/regression tests still pass. Reject "
                "fake failures, trivial commands, weakened tests, or irrelevant coverage. "
                "Developer claims are not proof. Explain missing evidence. Phase labels alone "
                "do not prove that tests were written before production code.",
            ),
            (
                "human",
                f"Task: {prompt}\nCriteria: {diagnosis}\nDelivery: {delivery}\nActual executions: {evidence}",
            ),
        ]
    )
