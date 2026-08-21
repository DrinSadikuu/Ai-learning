import asyncio

from app.core.tracing import setup_tracing


setup_tracing()


from evaluations.judge import llm_judge


TEST_CASES = [
    {
        "question": "What is the capital of France?",
        "expected_answer": "The capital of France is Paris.",
        "answer": "The capital of France is Berlin.",
    },
    {
        "question": "What does HTTP stand for?",
        "expected_answer": "HTTP stands for Hypertext Transfer Protocol.",
        "answer": "Python is a programming language.",
    },
    {
        "question": "What is Python?",
        "expected_answer": (
            "Python is a high-level general-purpose "
            "programming language."
        ),
        "answer": (
            "Python is a high-level general-purpose programming "
            "language used for software development."
        ),
    },
]


async def test_judge():
    for index, test_case in enumerate(
        TEST_CASES,
        start=1,
    ):
        result = await llm_judge.evaluate(
            question=test_case["question"],
            answer=test_case["answer"],
            expected_answer=test_case["expected_answer"],
        )

        overall_score = (
            result.correctness
            + result.relevance
            + result.conciseness
        ) / 3

        passed = (
            result.correctness >= 70
            and result.relevance >= 70
            and overall_score >= 70
        )

        print("=" * 70)
        print(f"Test {index}")
        print(f"Question: {test_case['question']}")
        print(f"Answer being tested: {test_case['answer']}")
        print()
        print(f"Correctness: {result.correctness}/100")
        print(f"Relevance: {result.relevance}/100")
        print(f"Conciseness: {result.conciseness}/100")
        print(f"Overall: {overall_score:.2f}/100")
        print(f"Reasoning: {result.reasoning}")
        print(
            f"Result: "
            f"{'PASS' if passed else 'FAIL'}"
        )


if __name__ == "__main__":
    asyncio.run(test_judge())