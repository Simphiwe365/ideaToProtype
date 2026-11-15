import os

from frontend.api_client import (
    estimate_cost_from_catalog,
    get_cost_breakdown,
    get_groq_api_key,
    should_use_direct_generation,
)
from frontend.pages.results import generate_plan_pdf


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
