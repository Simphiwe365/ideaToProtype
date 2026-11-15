"""Root-level Streamlit entry point for deployment compatibility."""

from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "llm-planner" / "frontend"

if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

if __name__ == "__main__":
    runpy.run_path(str(FRONTEND_DIR / "app.py"), run_name="__main__")
