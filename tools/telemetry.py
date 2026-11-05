import logging
import time
from contextlib import contextmanager


@contextmanager
def timed_event(name: str, run_id: str):
    started = time.monotonic()
    try:
        yield
    finally:
        logging.getLogger("agent.telemetry").info(
            "event=%s run_id=%s duration_s=%.3f", name, run_id, time.monotonic() - started
        )
