from typing import TypeVar

from pydantic import BaseModel

from config import openai
from prompts import EMAIL_ANALYSIS_PROMPT, JOB_ANALYSIS_PROMPT,REVIEW_ANALYSIS_PROMPT
from schemas import EmailAnalysis, JobAnalysis, ReviewAnalysis


T = TypeVar("T", bound=BaseModel)


def analyze_text(
    text: str,
    prompt: str,
    schema: type[T],
) -> T:
    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError("The text cannot be empty.")

    if len(cleaned_text) < 10:
        raise ValueError("The text is too short to analyze.")

    response = openai.responses.parse(
        model="gpt-5-nano",
        instructions=prompt,
        input=cleaned_text,
        text_format=schema,
    )

    parsed_result = response.output_parsed

    if parsed_result is None:
        raise ValueError("The AI did not return valid structured data.")

    return parsed_result


def analyze_job_description(job_description: str) -> JobAnalysis:
    return analyze_text(
        text=job_description,
        prompt=JOB_ANALYSIS_PROMPT,
        schema=JobAnalysis,
    )


def analyze_email(email_text: str) -> EmailAnalysis:
    return analyze_text(
        text=email_text,
        prompt=EMAIL_ANALYSIS_PROMPT,
        schema=EmailAnalysis,
    )

def analyze_review(review_text: str) -> ReviewAnalysis:
    return analyze_text(
        text=review_text,
        prompt=REVIEW_ANALYSIS_PROMPT,
        schema=ReviewAnalysis,
    )