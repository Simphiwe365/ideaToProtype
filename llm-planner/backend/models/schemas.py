"""Pydantic models for request and response schemas in the LLM planner API."""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class PlanRequest(BaseModel):
    """Request model for generating a manufacturing plan."""
    idea: str
    tools: List[str]
    materials: List[str]
    budget_zar: int
    skill_level: str  # "beginner", "intermediate", "advanced"
    include_3d_model: Optional[bool] = True  # Generate 3D model visualization


class PlanResponse(BaseModel):
    """Response model containing generated plans and estimates."""
    constrained_plan: str
    unconstrained_plan: str
    estimated_cost_zar: int
    steps: List[str]