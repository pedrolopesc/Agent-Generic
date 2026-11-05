import logging

logger = logging.getLogger("agent.monitor")


def monitor(state):
    status = (
        "completed"
        if state["approved"]
        else ("exhausted" if state["iteration"] >= state["max_iterations"] else "retrying")
    )
    logger.info("iteration=%s status=%s", state["iteration"], status)
    return {"status": status}
