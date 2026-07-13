from typing import Literal

from pydantic import BaseModel, Field


class JobAnalysis(BaseModel):
    job_title: str = Field(
        description="The job title mentioned or inferred from the description."
    )

    required_skills: list[str] = Field(
        description="Technical and professional skills required for the job."
    )

    minimum_experience_years: int = Field(
        ge=0,
        description="Minimum required years of experience. Use 0 if not specified."
    )

    seniority_level: Literal[
        "intern",
        "junior",
        "mid",
        "senior",
        "lead",
        "unknown",
    ] = Field(
        description="The seniority level required for the position."
    )

    remote: bool = Field(
        description="True when the position is remote, otherwise false."
    )

class EmailAnalysis(BaseModel):
    summary: str = Field(
        description="A short summary of the email."
    )

    sender_intent: str = Field(
        description="What the sender wants or expects."
    )

    urgency: Literal["low", "medium", "high"] = Field(
        description="How urgent the email is."
    )

    requires_response: bool = Field(
        description="Whether the recipient should respond."
    )

    action_items: list[str] = Field(
        description="Actions requested or implied by the email."
    )

class ReviewAnalysis(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        description="The overall sentiment of the review."
    )
    rating: int = Field(
        ge=1,
        le=5,
        description="An inferred rating from 1 to 5."
    )
    positive_points: list[str] = Field(
        description="Positive aspects mentioned in the review."
    )
    negative_points: list[str] = Field(
        description="Negative aspects mentioned in the review."
    )
    summary: str = Field(
        description="A concise summary of the review."
    )