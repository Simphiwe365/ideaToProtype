"""Router for the planner API endpoint."""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from models.schemas import PlanRequest, PlanResponse
from services.llm import generate_constrained_plan, generate_unconstrained_plan

router = APIRouter()
logger = logging.getLogger(__name__)


def estimate_cost_from_catalog(materials: list[str] | None = None, tools: list[str] | None = None) -> int:
    """Estimate cost from the JSON catalog of common materials and tools."""
    catalog_path = Path(__file__).resolve().parents[2] / "data" / "prices.json"
    if not catalog_path.exists():
        return 0

    with catalog_path.open("r", encoding="utf-8") as file:
        catalog = json.load(file)

    material_cost = sum(int(catalog.get("materials", {}).get(item.lower(), 0)) for item in materials or [])
    tool_cost = sum(int(catalog.get("tools", {}).get(item.lower(), 0)) for item in tools or [])
    return material_cost + tool_cost


@router.post("/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest) -> PlanResponse:
    """Generate constrained and unconstrained plans for a manufacturing idea."""
    logger.info(f"Received plan request for idea: {request.idea}")

    constrained = generate_constrained_plan(request)
    unconstrained = generate_unconstrained_plan(request.idea)

    estimated_cost = estimate_cost_from_catalog(request.materials, request.tools)
    if estimated_cost <= 0:
        estimated_cost = min(request.budget_zar, 1500)

    # Extract steps from constrained plan (simple parsing)
    steps = constrained.split('\n')[:5]  # First 5 lines as steps

    response = PlanResponse(
        constrained_plan=constrained,
        unconstrained_plan=unconstrained,
        estimated_cost_zar=estimated_cost,
        steps=steps,
    )

    logger.info("Plan generated successfully")
    return response