"""
Learning system for Mobius with privacy controls.

This package implements the meta-learning system that enables Mobius
to improve generation quality over time while maintaining strict privacy controls.
"""

from mobius.learning.private import PrivateLearningEngine
from mobius.learning.shared import SharedLearningEngine

__all__ = ["PrivateLearningEngine", "SharedLearningEngine"]
