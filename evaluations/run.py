import argparse
import json
from pathlib import Path

import httpx

from evaluations.metrics import summarize


def main():
    parser = argparse.ArgumentParser(description="Avalie tarefas na API real (consome tokens)")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    results = []
    dataset = Path(__file__).parent / "datasets" / "tasks.jsonl"
    with httpx.Client(
        base_url=args.url, timeout=1800, headers={"Authorization": f"Bearer {args.token}"}
    ) as client:
        for line in dataset.read_text(encoding="utf-8").splitlines():
            task = json.loads(line)
            prompt = task["prompt"] + "\nCritérios: " + "; ".join(task["criteria"])
            response = client.post("/runs", json={"prompt": prompt})
            response.raise_for_status()
            result = response.json()
            results.append(result)
            print(json.dumps({"task": task["id"], **result}, ensure_ascii=False))
    print(json.dumps(summarize(results)))


if __name__ == "__main__":
    main()
