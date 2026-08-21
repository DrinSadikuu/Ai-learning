import json
from pathlib import Path


RESULTS_DIR = Path("evaluations/results")

REGRESSION_THRESHOLD = 2.0


def load_json(path: Path) -> dict:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def compare_metric(
    name: str,
    previous: float,
    current: float,
):
    difference = current - previous

    print(
        f"{name}: "
        f"{previous:.2f} -> {current:.2f} "
        f"({difference:+.2f})"
    )

    return difference


def compare_runs():
    result_files = sorted(
        RESULTS_DIR.glob("*.json")
    )

    if len(result_files) < 2:
        print(
            "You need at least two evaluation "
            "result files to compare."
        )
        return

    previous_path = result_files[-2]
    current_path = result_files[-1]

    previous_run = load_json(previous_path)
    current_run = load_json(current_path)

    previous_summary = previous_run["summary"]
    current_summary = current_run["summary"]

    print("=" * 70)
    print("REGRESSION COMPARISON")
    print("=" * 70)

    print(f"Previous run: {previous_path.name}")
    print(f"Current run:  {current_path.name}")

    print()
    print(
        f"Previous model: "
        f"{previous_run['model']}"
    )
    print(
        f"Current model:  "
        f"{current_run['model']}"
    )

    print()
    print("-" * 70)
    print("METRICS")
    print("-" * 70)

    correctness_delta = compare_metric(
        name="Correctness",
        previous=previous_summary[
            "average_correctness"
        ],
        current=current_summary[
            "average_correctness"
        ],
    )

    relevance_delta = compare_metric(
        name="Relevance",
        previous=previous_summary[
            "average_relevance"
        ],
        current=current_summary[
            "average_relevance"
        ],
    )

    conciseness_delta = compare_metric(
        name="Conciseness",
        previous=previous_summary[
            "average_conciseness"
        ],
        current=current_summary[
            "average_conciseness"
        ],
    )

    overall_delta = compare_metric(
        name="Overall",
        previous=previous_summary[
            "average_overall"
        ],
        current=current_summary[
            "average_overall"
        ],
    )

    previous_pass_rate = (
        previous_summary["pass_rate"] * 100
    )

    current_pass_rate = (
        current_summary["pass_rate"] * 100
    )

    pass_rate_delta = compare_metric(
        name="Pass rate",
        previous=previous_pass_rate,
        current=current_pass_rate,
    )

    deltas = {
        "correctness": correctness_delta,
        "relevance": relevance_delta,
        "conciseness": conciseness_delta,
        "overall": overall_delta,
        "pass_rate": pass_rate_delta,
    }

    regressions = {
        name: delta
        for name, delta in deltas.items()
        if delta < -REGRESSION_THRESHOLD
    }

    improvements = {
        name: delta
        for name, delta in deltas.items()
        if delta > REGRESSION_THRESHOLD
    }

    print()
    print("-" * 70)
    print("RESULT")
    print("-" * 70)

    if regressions:
        print("REGRESSION DETECTED")

        for name, delta in regressions.items():
            print(
                f"- {name}: "
                f"{delta:+.2f}"
            )
    else:
        print(
            "No significant regression detected."
        )

    if improvements:
        print()
        print("Improvements:")

        for name, delta in improvements.items():
            print(
                f"- {name}: "
                f"{delta:+.2f}"
            )


if __name__ == "__main__":
    compare_runs()