"""API client for communicating with the backend service."""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def get_plan(data: dict) -> dict:
    """Send a plan request to the backend and return the response."""
    url = f"{BACKEND_URL}/api/plan"
    try:
        response = httpx.post(url, json=data, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise Exception(f"Request error: {str(e)}")