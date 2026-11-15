import os

from frontend.api_client import (
    estimate_cost_from_catalog,
    get_cost_breakdown,
    get_groq_api_key,
    should_use_direct_generation,
)
from frontend.pages.results import clean_plan_text, generate_plan_pdf


def test_frontend_imports_work_when_frontend_root_is_on_path(monkeypatch):
    import importlib.util
    import sys
    from pathlib import Path

    module_path = Path(__file__).resolve().parents[1] / "frontend" / "app.py"
    sys.path.insert(0, str(module_path.parent))
    spec = importlib.util.spec_from_file_location("streamlit_frontend_app", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, "planner_main")
    assert hasattr(module, "results_main")


def test_localhost_backend_uses_direct_generation(monkeypatch):
    monkeypatch.delenv("BACKEND_URL", raising=False)
    assert should_use_direct_generation() is True

    monkeypatch.setenv("BACKEND_URL", "http://localhost:8000")
    assert should_use_direct_generation() is True


def test_public_backend_uses_http_call(monkeypatch):
    monkeypatch.setenv("BACKEND_URL", "https://example-backend.onrender.com")
    assert should_use_direct_generation() is False


def test_get_groq_api_key_supports_nested_streamlit_secrets(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr("frontend.api_client.load_dotenv", lambda *args, **kwargs: None)
    monkeypatch.setattr("frontend.api_client.secrets", {"general": {"GROQ_API_KEY": "nested-secret-key"}}, raising=False)
    assert get_groq_api_key() == "nested-secret-key"


def test_materials_and_tools_use_catalog_prices():
    total = estimate_cost_from_catalog(["wood", "glue"], ["saw"])
    assert total == 123


def test_available_materials_and_tools_are_excluded_from_cost():
    total = estimate_cost_from_catalog(
        ["wood", "metal", "glue"],
        ["saw", "drill"],
        available_materials=["wood"],
        available_tools=["saw"],
    )
    assert total == 258


def test_cost_breakdown_lists_items_with_prices():
    breakdown = get_cost_breakdown(
        ["wood", "metal", "glue"],
        ["saw", "drill"],
        available_materials=["wood"],
        available_tools=["saw"],
    )
    assert breakdown["total"] == 258
    assert breakdown["materials"] == [{"name": "metal", "price": 120}, {"name": "glue", "price": 18}]
    assert breakdown["tools"] == [{"name": "drill", "price": 120}]


def test_plan_pdf_download_is_generated():
    request = {
        "idea": "Simple bench",
        "budget_zar": 1000,
        "skill_level": "beginner",
        "tools": ["saw"],
        "materials": ["wood"],
        "available_tools": [],
        "available_materials": [],
    }
    result = {
        "constrained_plan": "Cut the wood to size and sand the edges.",
        "unconstrained_plan": "Use a more advanced build with a finish coat.",
        "estimated_cost_zar": 350,
    }

    pdf_bytes = generate_plan_pdf(request, result)

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 1000


def test_clean_plan_text_removes_duplicate_cost_lines():
    raw_text = """Manufacturing Plan
Generated: 2026-06-03 22:43:37
PROJECT DETAILS
Field Value
Idea simple bench
Skill Level beginner
Budget R500
Estimated Cost R500

CONSTRAINED PLAN
PROTOTYPE DESCRIPTION: ...

**Estimated Cost:** R45
"""

    cleaned = clean_plan_text(raw_text)

    assert "Estimated Cost R500" in cleaned
    assert "**Estimated Cost:** R45" not in cleaned
    assert "Estimated Cost:" not in cleaned.split("PROJECT DETAILS")[-1].split("CONSTRAINED PLAN")[0]


def test_clean_plan_text_removes_duplicate_plan_blocks():
    raw_text = """Manufacturing Plan
Generated: 2026-11-15 14:15:51
PROJECT DETAILS
Field Value
Idea pc wooden stand
Skill Level Beginner
Budget R500
Tools hand tools
Materials wood
Estimated Cost R45
CONSTRAINED PLAN
UNCONSTRAINED PLAN
Manufacturing Plan
Generated: 2026-11-15 09:27:42
PROJECT DETAILS
Field Value
Idea pc wooden stand
Skill Level beginner
Budget R500
Tools hand saw, sandpaper, screwdriver (owned), wooden glue (owned)
Materials pine timber, plywood, wood screws, clear varnish, wooden glue (owned)
Estimated Cost R500
UNCONSTRAINED PLAN
PROTOTYPE DESCRIPTION: A simple wooden desk stand that holds a PC monitor on a top shelf and a keyboard on a lower shelf.
"""

    cleaned = clean_plan_text(raw_text)

    assert cleaned.count("Manufacturing Plan") == 1
    assert "CONSTRAINED PLAN" in cleaned
    assert "UNCONSTRAINED PLAN" in cleaned
    assert "Budget R500" in cleaned


def test_plan_completion_checker_requires_final_sections():
    from frontend.api_client import _is_plan_complete

    incomplete = """Manufacturing Plan
Generated: 2026-11-15 14:30:00
PROJECT DETAILS
Field Value
Idea wooden laptop stand
Skill Level Beginner
Budget R500
Tools hand tools
Materials wood
Estimated Cost R45
CONSTRAINED PLAN
PROTOTYPE DESCRIPTION: A simple design.
BUILD STEPS:
STEP 1: Cut wood.
- Tools/Materials needed for this step: hand saw
- How to do it:
1. Measure the board.
2. Cut it.
3. Sand it.
- Measurement check: 200 mm.
- Safety warning: Wear gloves.
- Time needed: 15 min
"""

    complete = incomplete + "\nSTEP 2: Assemble pieces.\n- Tools/Materials needed for this step: wood glue\n- How to do it:\n1. Apply glue.\n2. Align pieces.\n3. Clamp them.\n- Measurement check: All edges match.\n- Safety warning: Keep fingers clear.\n- Time needed: 20 min\n\nSTEP 3: Sand and finish.\n- Tools/Materials needed for this step: sandpaper\n- How to do it:\n1. Sand edges.\n2. Clean dust.\n3. Apply finish.\n- Measurement check: Surface is smooth.\n- Safety warning: Wear dust mask.\n- Time needed: 20 min\n\nSTEP 4: Fit the stand.\n- Tools/Materials needed for this step: clamp\n- How to do it:\n1. Place the stand.\n2. Check balance.\n3. Tighten if needed.\n- Measurement check: The base is level.\n- Safety warning: Check for sharp edges.\n- Time needed: 10 min\n\nSTEP 5: Test the stand.\n- Tools/Materials needed for this step: measuring tape\n- How to do it:\n1. Place laptop.\n2. Confirm fit.\n3. Adjust.\n- Measurement check: The laptop sits level.\n- Safety warning: Test on a flat table.\n- Time needed: 10 min\n\nSTEP 6: Finish and inspect.\n- Tools/Materials needed for this step: cloth, finish\n- How to do it:\n1. Wipe the finish.\n2. Inspect joints.\n3. Clean the work area.\n- Measurement check: Surface is even and stable.\n- Safety warning: Allow finish to dry fully.\n- Time needed: 15 min\n\nFINAL CHECKLIST:\n- Check measurements.\n- Confirm stability.\n- Sand sharp edges.\n- Test the laptop fit.\n\nREPAIRABILITY TIP: Keep a small sanding block ready.\nSAFETY NOTE: Wear goggles and work in a ventilated area."

    assert _is_plan_complete(incomplete) is False
    assert _is_plan_complete(complete) is True
