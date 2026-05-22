"""Router for the planner API endpoint."""

import logging
from fastapi import APIRouter, HTTPException
from models.schemas import PlanRequest, PlanResponse
from services.llm import generate_constrained_plan, generate_unconstrained_plan
from services.model_3d import generate_3d_model_config

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest) -> PlanResponse:
    """Generate constrained and unconstrained plans for a manufacturing idea."""
    logger.info(f"Received plan request for idea: {request.idea}")

    constrained = generate_constrained_plan(request)
    unconstrained = generate_unconstrained_plan(request.idea)

    # Simple cost estimation (placeholder logic)
    estimated_cost = min(request.budget_zar, 1500)  # Cap at 1500 for demo

    # Extract steps from constrained plan (simple parsing)
    steps = constrained.split('\n')[:5]  # First 5 lines as steps

    # Generate 3D model configuration if requested
    model_3d_config = None
    if request.include_3d_model:
        try:
            model_3d_config = generate_3d_model_config(request.idea, constrained, request.materials)
            logger.info("3D model configuration generated successfully")
        except Exception as e:
            logger.warning(f"Failed to generate 3D model config: {str(e)}")

    response = PlanResponse(
        constrained_plan=constrained,
        unconstrained_plan=unconstrained,
        estimated_cost_zar=estimated_cost,
        steps=steps,
        model_3d_config=model_3d_config
    )

    logger.info("Plan generated successfully")
    return response