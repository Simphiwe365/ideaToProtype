"""Pydantic models for request and response schemas in the LLM planner API."""

from pydantic import BaseModel
from typing import List


class PlanRequest(BaseModel):
    """Request model for generating a manufacturing plan."""
    idea: str
    tools: List[str]
    materials: List[str]
    budget_zar: int
    skill_level: str  # "beginner", "intermediate", "advanced"


class PlanResponse(BaseModel):
    """Response model containing generated plans and estimates."""
    constrained_plan: str
    unconstrained_plan: str
    estimated_cost_zar: int
    steps: List[str]