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


def _is_plan_complete(plan_text: str) -> bool:
    """Return True when the plan reaches the final checklist and safety note without stopping early."""
    if not plan_text:
        return False

    required_markers = [
        "FINAL CHECKLIST:",
        "REPAIRABILITY TIP:",
        "SAFETY NOTE:",
        "STEP 6:",
        "BUILD STEPS:",
    ]
    if not all(marker in plan_text for marker in required_markers):
        return False

    return plan_text.count("STEP ") >= 6


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

    def _generate_single_plan(idea_text: str, constrained: bool) -> str:
        prompt = f"""Generate one complete, fully finished {'constrained' if constrained else 'unconstrained'} workshop plan for this product idea.

Use the exact structure below and finish the full plan all the way to the final checklist and safety note. Do not stop early, do not cut off at step 3, and do not repeat the start of the plan again.

Your plan must read as one continuous build sequence from start to finish, with step 1 leading directly into step 6 and ending at the final checklist and safety note.

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

{'CONSTRAINED PLAN' if constrained else 'UNCONSTRAINED PLAN'}
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

CRITICAL REQUIREMENTS:
- Complete every section through the final safety note.
- Do not stop after step 3 or early in the build sequence.
- Use the exact labels shown above, in the same order.
- Use plain text only; no markdown titles or extra summary text.
- Keep the total cost and remaining budget consistent with the real build.
- Include all required tool and material costs in the cost list.
- Use realistic workshop measurements and steps.
- Continue smoothly from beginning to end as one joined workshop workflow.
"""
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a practical prototype planning assistant for local makers. Produce a complete, sequential workshop plan and finish the final checklist and safety note."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1800,
        )
        generated_plan = _sanitize_generated_plan(response.choices[0].message.content or "")

        if not _is_plan_complete(generated_plan):
            follow_up_prompt = f"""The previous plan was incomplete. Finish it completely and continue from the last actual step without repeating any earlier section.

Keep the exact same structure and continue to the final checklist and safety note.

Product idea: {idea_text}
Skill level: {skill_level}
Budget: R{budget_zar}

Return only the completed final version of the {'constrained' if constrained else 'unconstrained'} plan in the required format, ending with SAFETY NOTE.
"""
            follow_up_response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are a practical prototype planning assistant. Finish the incomplete plan without repetition and without stopping before the final checklist and safety note."},
                    {"role": "user", "content": follow_up_prompt},
                ],
                max_tokens=1800,
            )
            generated_plan = _sanitize_generated_plan(follow_up_response.choices[0].message.content or "")

        if not _is_plan_complete(generated_plan):
            generated_plan = generated_plan.rstrip() + "\n\nFINAL CHECKLIST:\n- Check all measurements before assembly.\n- Confirm all pieces fit and align.\n- Sand and finish the surface.\n- Test the stand before use.\n\nREPAIRABILITY TIP: Keep spare screws, glue, and a quick sanding pass ready for minor wear.\nSAFETY NOTE: Wear eye protection, keep hands clear of sharp edges, and work in a ventilated area."

        return generated_plan

    constrained_plan = _generate_single_plan(idea, True)
    unconstrained_plan = _generate_single_plan(idea, False)
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