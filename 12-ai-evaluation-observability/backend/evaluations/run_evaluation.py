import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import get_settings
from app.core.tracing import setup_tracing


setup_tracing()


from app.services.llm_service import llm_service
from evaluations.dataset import EVALUATION_DATASET
from evaluations.judge import llm_judge


RESULTS_DIR = Path("evaluations/results")


async def run_evaluation():
    settings = get_settings()

    total_tests = len(EVALUATION_DATASET)

    passed_tests = 0

    total_correctness = 0
    total_relevance = 0
    total_conciseness = 0
    total_overall = 0

    test_results = []

    for index, test_case in enumerate(
        EVALUATION_DATASET,
        start=1,
    ):
        question = test_case["question"]
        expected_answer = test_case["expected_answer"]

        answer = await llm_service.generate(
            question=question,
        )

        judge_result = await llm_judge.evaluate(
            question=question,
            answer=answer,
            expected_answer=expected_answer,
        )

        correctness = judge_result.correctness
        relevance = judge_result.relevance
        conciseness = judge_result.conciseness

        overall_score = (
            correctness
            + relevance
            + conciseness
        ) / 3

        passed = (
            correctness >= 70
            and relevance >= 70
            and overall_score >= 70
        )

        if passed:
            passed_tests += 1

        total_correctness += correctness
        total_relevance += relevance
        total_conciseness += conciseness
        total_overall += overall_score

        test_results.append(
            {
                "question": question,
                "expected_answer": expected_answer,
                "answer": answer,
                "correctness": correctness,
                "relevance": relevance,
                "conciseness": conciseness,
                "overall_score": round(
                    overall_score,
                    2,
                ),
                "passed": passed,
                "reasoning": judge_result.reasoning,
            }
        )

        print("=" * 70)
        print(f"Test {index}")
        print(f"Question: {question}")
        print(f"Expected answer: {expected_answer}")
        print(f"AI answer: {answer}")
        print()
        print(f"Correctness: {correctness}/100")
        print(f"Relevance: {relevance}/100")
        print(f"Conciseness: {conciseness}/100")
        print(
            f"Overall score: "
            f"{overall_score:.2f}/100"
        )
        print(
            f"Reasoning: "
            f"{judge_result.reasoning}"
        )
        print(
            f"Result: "
            f"{'PASS' if passed else 'FAIL'}"
        )

    failed_tests = total_tests - passed_tests

    average_correctness = (
        total_correctness / total_tests
    )

    average_relevance = (
        total_relevance / total_tests
    )

    average_conciseness = (
        total_conciseness / total_tests
    )

    average_overall = (
        total_overall / total_tests
    )

    pass_rate = passed_tests / total_tests

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Pass rate: {pass_rate:.2%}")

    print(
        f"Average correctness: "
        f"{average_correctness:.2f}/100"
    )

    print(
        f"Average relevance: "
        f"{average_relevance:.2f}/100"
    )

    print(
        f"Average conciseness: "
        f"{average_conciseness:.2f}/100"
    )

    print(
        f"Average overall score: "
        f"{average_overall:.2f}/100"
    )

    results = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "model": settings.openai_model,
        "summary": {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": round(
                pass_rate,
                4,
            ),
            "average_correctness": round(
                average_correctness,
                2,
            ),
            "average_relevance": round(
                average_relevance,
                2,
            ),
            "average_conciseness": round(
                average_conciseness,
                2,
            ),
            "average_overall": round(
                average_overall,
                2,
            ),
        },
        "tests": test_results,
    }

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        datetime.now(timezone.utc)
        .strftime("%Y%m%d_%H%M%S")
        + ".json"
    )

    result_path = RESULTS_DIR / filename

    with result_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(
        f"Results saved to: "
        f"{result_path}"
    )


if __name__ == "__main__":
    asyncio.run(run_evaluation())