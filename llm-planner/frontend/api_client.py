"""API client for communicating with the backend service."""

import json
import os
import re
from pathlib import Path

import httpx
from dotenv import load_dotenv

try:
    from streamlit import secrets
except ImportError:  # pragma: no cover - Streamlit is not required in local scripts.
    secrets = None

from groq import Groq

load_dotenv()


def get_price_catalog_path() -> Path:
    """Return the path to the shared JSON price catalog."""
    return Path(__file__).resolve().parent.parent / "data" / "prices.json"


def load_price_catalog() -> dict:
    """Load the material and tool price list used for cost estimation."""
    catalog_path = get_price_catalog_path()
    if not catalog_path.exists():
        return {"materials": {}, "tools": {}}

    with catalog_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        return {"materials": {}, "tools": {}}

    return data


def _normalise_item_name(item: str) -> str:
    """Normalise a catalog item name for comparisons."""
    return str(item).strip().lower()


def _normalise_item_list(items: list[str] | None) -> list[str]:
    """Convert a list of item names to lowercase, stripped values."""
    return [
        _normalise_item_name(item)
        for item in (items or [])
        if _normalise_item_name(item)
    ]


def _remove_available_items(selected_items: list[str] | None, available_items: list[str] | None) -> list[str]:
    """Return only the selected items that are not already available."""
    selected = _normalise_item_list(selected_items)
    available = set(_normalise_item_list(available_items))
    return [item for item in selected if item not in available]


def get_cost_breakdown(
    materials: list[str] | None = None,
    tools: list[str] | None = None,
    available_materials: list[str] | None = None,
    available_tools: list[str] | None = None,
) -> dict:
    """Return a breakdown of the still-needed materials and tools with their prices."""
    catalog = load_price_catalog()
    missing_materials = _remove_available_items(materials, available_materials)
    missing_tools = _remove_available_items(tools, available_tools)

    material_items = [{
        "name": item,
        "price": int(catalog.get("materials", {}).get(item, 0)),
    } for item in missing_materials]
    tool_items = [{
        "name": item,
        "price": int(catalog.get("tools", {}).get(item, 0)),
    } for item in missing_tools]

    total = sum(item["price"] for item in material_items) + sum(item["price"] for item in tool_items)
    return {
        "materials": material_items,
        "tools": tool_items,
        "total": total,
    }


def estimate_cost_from_catalog(
    materials: list[str] | None = None,
    tools: list[str] | None = None,
    available_materials: list[str] | None = None,
    available_tools: list[str] | None = None,
) -> int:
    """Estimate total cost from materials and tools that are still needed."""
    return get_cost_breakdown(
        materials,
        tools,
        available_materials=available_materials,
        available_tools=available_tools,
    )["total"]


def get_backend_url() -> str | None:
    """Read the configured backend URL, or return None when the app should run standalone."""
    url = os.getenv("BACKEND_URL")
    if url is None:
        return None
    return url.strip().rstrip("/")


def should_use_direct_generation() -> bool:
    """Use the direct Groq path when running locally or in a single-app deployment."""
    backend_url = get_backend_url()
    if backend_url is None:
        return True
    return backend_url.startswith("http://localhost") or backend_url.startswith("http://127.0.0.1") or backend_url.startswith("http://0.0.0.0") or backend_url.startswith("http://backend:")


def get_groq_api_key() -> str | None:
    """Read the Groq API key from env vars or Streamlit secrets."""
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return api_key

    env_file = Path(__file__).resolve().parent.parent / "backend" / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            return api_key

    if secrets is not None:
        try:
            direct_value = secrets.get("GROQ_API_KEY")
            if direct_value:
                return direct_value
        except Exception:
            direct_value = None

        try:
            general_section = secrets.get("general") or {}
            if isinstance(general_section, dict):
                nested_value = general_section.get("GROQ_API_KEY")
                if nested_value:
                    return nested_value
        except Exception:
            pass

        try:
            return secrets["general"]["GROQ_API_KEY"]
        except Exception:
            return None

    return None


def generate_direct_plan(data: dict) -> dict:
    """Generate plans directly in Streamlit without requiring a separate backend service."""
    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Add it as a Streamlit secret or environment variable.")

    client = Groq(api_key=api_key)
    idea = data.get("idea", "")
    available_tools = data.get("available_tools", []) or []
    available_materials = data.get("available_materials", []) or []
    required_tools = _remove_available_items(data.get("tools", []), available_tools)
    required_materials = _remove_available_items(data.get("materials", []), available_materials)
    tool_summary = ", ".join(required_tools) or "none"
    material_summary = ", ".join(required_materials) or "none"
    available_tool_summary = ", ".join(available_tools) or "none"
    available_material_summary = ", ".join(available_materials) or "none"
    budget_zar = int(data.get("budget_zar", 0))
    skill_level = data.get("skill_level", "beginner")
    cost_breakdown = get_cost_breakdown(
        data.get("materials", []),
        data.get("tools", []),
        available_materials=available_materials,
        available_tools=available_tools,
    )
    estimated_cost = cost_breakdown["total"]
    if estimated_cost < 0:
        estimated_cost = 0

    def _sanitize_generated_plan(plan_text: str) -> str:
        """Remove duplicate Manufacturing Plan blocks and mixed plan sections."""
        if not plan_text:
            return ""

        cleaned = plan_text.replace("\r\n", "\n").replace("\r", "\n").strip()
        manufacturing_matches = list(re.finditer(r"(?m)^Manufacturing Plan\s*$", cleaned))
        if len(manufacturing_matches) > 1:
            cleaned = cleaned[manufacturing_matches[-1].start():].strip()

        if "CONSTRAINED PLAN" in cleaned and "UNCONSTRAINED PLAN" in cleaned:
            constrained_start = cleaned.index("CONSTRAINED PLAN")
            unconstrained_start = cleaned.index("UNCONSTRAINED PLAN")
            if unconstrained_start > constrained_start:
                cleaned = cleaned[constrained_start:unconstrained_start].rstrip()

        return cleaned.strip()

    def _generate_combined_plan(idea_text: str) -> str:
        prompt = f"""Generate one complete workshop plan document for this product idea using the exact structure and labels below.

The response must contain both the constrained and unconstrained plan sections in this exact order:
1. Manufacturing Plan
2. PROJECT DETAILS
3. CONSTRAINED PLAN
4. UNCONSTRAINED PLAN

Do not add any extra headings, summary text, or markdown formatting.

INPUT CONTEXT:
IDEA: {idea_text}
TOOLS TO USE: {tool_summary}
TOOLS ALREADY AVAILABLE: {available_tool_summary}
MATERIALS TO USE: {material_summary}
MATERIALS ALREADY AVAILABLE: {available_material_summary}
BUDGET: R{budget_zar} maximum total
SKILL LEVEL: {skill_level}

OUTPUT FORMAT EXACTLY AS FOLLOWS:

Manufacturing Plan
Generated: [current date and time in YYYY-MM-DD HH:MM:SS format]
PROJECT DETAILS
Field Value
Idea [exact product concept]
Skill Level [skill level]
Budget R[amount]
Tools [required tools and any already owned tools]
Materials [required materials and any already owned materials]
Estimated Cost R[total cost in ZAR]

CONSTRAINED PLAN
PROTOTYPE DESCRIPTION: [1-2 clear sentences explaining the prototype and what it does]
REQUIRED TOOLS AND MATERIALS:
- [Item name] ([quantity]): R[price] × [quantity] = R[total]
* [reason it is needed]
- [Item name] ([quantity]): R[price] × [quantity] = R[total]
* [reason it is needed]
SUBTOTAL FOR MATERIALS & TOOLS: R[total]
REMAINING BUDGET: R[remaining amount]
BUILD STEPS:
STEP 1: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

STEP 2: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

STEP 3: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

STEP 4: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

STEP 5: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

STEP 6: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

FINAL CHECKLIST:
- [final checklist item 1]
- [final checklist item 2]
- [final checklist item 3]
- [final checklist item 4]

REPAIRABILITY TIP: [one practical repair tip]
SAFETY NOTE: [one safety note]

UNCONSTRAINED PLAN
PROTOTYPE DESCRIPTION: [1-2 clear sentences explaining the optimal version]
REQUIRED TOOLS AND MATERIALS:
- [Item name] ([quantity]): R[price] × [quantity] = R[total]
* [reason it is needed]
- [Item name] ([quantity]): R[price] × [quantity] = R[total]
* [reason it is needed]
SUBTOTAL FOR MATERIALS & TOOLS: R[total]
REMAINING BUDGET: R[remaining amount]
BUILD STEPS:
STEP 1: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

STEP 2: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

STEP 3: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

STEP 4: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

STEP 5: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

STEP 6: [short title].
- Tools/Materials needed for this step: [exact items]
- How to do it:
1. [exact step 1]
2. [exact step 2]
3. [exact step 3]
- Measurement check: [specific measurement or size to verify]
- Safety warning: [specific safety reminder]
- Time needed: [time]

FINAL CHECKLIST:
- [final checklist item 1]
- [final checklist item 2]
- [final checklist item 3]
- [final checklist item 4]

REPAIRABILITY TIP: [one practical repair tip]
SAFETY NOTE: [one safety note]

STRICT RULES:
- Use exactly the labels and order shown above.
- Keep plain text only; no markdown, no bold, no extra summary text.
- Include realistic measurements in mm or cm where relevant.
- Every required tool/material must be listed with a cost line like "Item (1): R10 × 1 = R10".
- Keep the final total aligned with the subtotal and budget.
- If the plan exceeds budget, state the overage clearly in REMAINING BUDGET.
- Use practical workshop language.
- Produce both the constrained and unconstrained plan sections in one final response.
- Do not invent extra sections outside the template.
"""
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a practical prototype planning assistant for local makers. Produce clear, sequential workshop instructions that are easy to follow on a bench or in a small workshop."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
        )
        return _sanitize_generated_plan(response.choices[0].message.content or "")

    full_plan = _generate_combined_plan(idea)
    constrained_start = full_plan.find("CONSTRAINED PLAN")
    unconstrained_start = full_plan.find("UNCONSTRAINED PLAN")

    if constrained_start != -1 and unconstrained_start != -1 and unconstrained_start > constrained_start:
        constrained_plan = full_plan[full_plan.find("Manufacturing Plan"):unconstrained_start].strip()
        unconstrained_plan = full_plan[unconstrained_start:].strip()
    else:
        constrained_plan = _sanitize_generated_plan(full_plan)
        unconstrained_plan = _sanitize_generated_plan(full_plan)

    steps = [step.strip() for step in constrained_plan.splitlines() if step.strip()][:5]

    return {
        "constrained_plan": constrained_plan,
        "unconstrained_plan": unconstrained_plan,
        "estimated_cost_zar": estimated_cost,
        "cost_breakdown": cost_breakdown,
        "steps": steps,
        "model_3d_config": None,
    }
    steps = [step.strip() for step in constrained_plan.splitlines() if step.strip()][:5]

    return {
        "constrained_plan": constrained_plan,
        "unconstrained_plan": unconstrained_plan,
        "estimated_cost_zar": estimated_cost,
        "cost_breakdown": cost_breakdown,
        "steps": steps,
        "model_3d_config": None,
    }


def get_plan(data: dict) -> dict:
    """Send a plan request to the backend service or generate it directly for one-app deployments."""
    if should_use_direct_generation():
        return generate_direct_plan(data)

    backend_url = get_backend_url()
    if not backend_url:
        raise ValueError("No backend URL configured.")

    url = f"{backend_url}/api/plan"
    try:
        response = httpx.post(url, json=data, timeout=180.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise Exception(f"Request error: {str(e)}")