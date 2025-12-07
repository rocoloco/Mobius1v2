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
    
    @classmethod
    def model_validate(cls, obj):
        """Normalize severity to lowercase before validation."""
        if isinstance(obj, dict) and "severity" in obj:
            obj["severity"] = obj["severity"].lower()
        return super().model_validate(obj)


class CategoryScore(BaseModel):
    """Compliance score for a specific category."""

    category: str = Field(description="Category name (colors, typography, layout, logo_usage)")
    score: float = Field(description="Score from 0-100")
    passed: bool = Field(description="Whether this category passed compliance threshold")
    violations: List[Violation] = Field(default_factory=list, description="List of violations")

    def model_post_init(self, __context):
        """Validate score is in valid range."""
        if not 0 <= self.score <= 100:
            raise ValueError(f"Score must be between 0 and 100, got {self.score}")


class ComplianceScore(BaseModel):
    """Overall compliance score with category breakdowns."""

    overall_score: float = Field(description="Weighted average of all categories (0-100)")
    categories: List[CategoryScore] = Field(description="Individual category scores")
    approved: bool = Field(description="Whether asset is approved for use")
    summary: str = Field(description="Overall assessment summary")

    def model_post_init(self, __context):
        """Validate overall_score is in valid range."""
        if not 0 <= self.overall_score <= 100:
            raise ValueError(f"Overall score must be between 0 and 100, got {self.overall_score}")
