def summarize(results: list[dict]) -> dict:
    count = len(results)
    return {
        "tasks": count,
        "completion_rate": sum(r["status"] == "completed" for r in results) / count if count else 0,
        "mean_iterations": sum(r["iteration"] for r in results) / count if count else 0,
    }
