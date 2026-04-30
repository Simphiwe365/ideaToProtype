"""LLM service module for generating manufacturing plans using Ollama local API."""

import ollama
import httpx
from models.schemas import PlanRequest

# Model name for Ollama
MODEL_NAME = "llama3.1:8b"

# FIX: Create httpx Timeout object - this is the correct way to set timeout for Ollama client
# The timeout parameter is passed directly to ollama.Client() constructor, not to .chat()
_timeout = httpx.Timeout(120.0)


def generate_constrained_plan(request: PlanRequest) -> str:
    """Generate a constrained manufacturing plan based on user inputs."""
    prompt = f"""
    Generate a detailed manufacturing plan for the following product idea, considering the given constraints:

    Product Idea: {request.idea}
    Available Tools: {', '.join(request.tools)}
    Available Materials: {', '.join(request.materials)}
    Budget: R{request.budget_zar}
    Skill Level: {request.skill_level}

    Provide a step-by-step plan that respects these constraints. Focus on feasibility within the budget and skill level.
    """
    try:
        # FIX: Pass timeout to ollama.Client() constructor (not to .chat())
        # The ollama library accepts timeout directly in the constructor via BaseClient
        client = ollama.Client(host="http://127.0.0.1:11434", timeout=_timeout)
        response = client.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.7, "num_predict": 400},
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return f"Error generating constrained plan: {str(e)}"


def generate_unconstrained_plan(idea: str) -> str:
    """Generate an unconstrained manufacturing plan for the product idea."""
    prompt = f"""
    Generate a creative and detailed manufacturing plan for the following product idea without any constraints:

    Product Idea: {idea}

    Provide a comprehensive step-by-step plan with innovative approaches.
    """
    try:
        # FIX: Pass timeout to ollama.Client() constructor (not to .chat())
        # The ollama library accepts timeout directly in the constructor via BaseClient
        client = ollama.Client(host="http://127.0.0.1:11434", timeout=_timeout)
        response = client.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.7, "num_predict": 400},
        )
        return response["message"]["content"].strip()
    except Exception as e:
        return f"Error generating unconstrained plan: {str(e)}"
