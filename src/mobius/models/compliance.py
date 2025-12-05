"""
Compliance scoring models.

Defines structures for detailed compliance scoring with category breakdowns.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List
from enum import Enum


class Severity(str, Enum):
    """Violation severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Violation(BaseModel):
    """A specific compliance violation."""

    category: str = Field(description="Category where violation occurred")
    description: str = Field(description="Detailed description of the violation")
    severity: Severity = Field(description="Severity level of the violation")
    fix_suggestion: str = Field(description="Suggested fix for the violation")


class CategoryScore(BaseModel):
    """Compliance score for a specific category."""

    category: str = Field(description="Category name (colors, typography, layout, logo_usage)")
    score: float = Field(ge=0, le=100, description="Score from 0-100")
    passed: bool = Field(description="Whether this category passed compliance threshold")
    violations: List[Violation] = Field(default_factory=list, description="List of violations")


class ComplianceScore(BaseModel):
    """Overall compliance score with category breakdowns."""

    overall_score: float = Field(ge=0, le=100, description="Weighted average of all categories")
    categories: List[CategoryScore] = Field(description="Individual category scores")
    approved: bool = Field(description="Whether asset is approved for use")
    summary: str = Field(description="Overall assessment summary")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "overall_score": 85.5,
                "categories": [
                    {
                        "category": "colors",
                        "score": 90.0,
                        "passed": True,
                        "violations": [],
                    },
                    {
                        "category": "typography",
                        "score": 75.0,
                        "passed": False,
                        "violations": [
                            {
                                "category": "typography",
                                "description": "Font family does not match brand guidelines",
                                "severity": "medium",
                                "fix_suggestion": "Use Arial or Helvetica",
                            }
                        ],
                    },
                ],
                "approved": True,
                "summary": "Asset meets brand standards with minor typography issues",
            }
        }
    )
