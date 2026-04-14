"""LLM service module for generating manufacturing plans using Groq API."""

import os
from groq import Groq
from dotenv import load_dotenv
from models.schemas import PlanRequest

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


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
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
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
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating unconstrained plan: {str(e)}"