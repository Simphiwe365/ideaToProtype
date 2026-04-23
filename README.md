# LLM-Guided Micro-Manufacturing Planner

A proof-of-concept web application for generating LLM-guided manufacturing plans with separated frontend and backend.

## Project Overview

This application allows local makers to input a product idea and local constraints, receiving an LLM-generated prototype plan. The architecture strictly separates the backend (FastAPI) and frontend (Streamlit).

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Ollama installed and running locally (download from https://ollama.ai/)
- LLaMA 3.1 8B model pulled in Ollama (`ollama pull llama3.1:8b`)

### Environment Setup
1. Clone or download this repository.
2. Navigate to the `llm-planner` directory.
3. Ensure Ollama is running locally and the `llama3.1:8b` model is pulled.
4. Ensure `frontend/.env` has `BACKEND_URL=http://localhost:8000` (or adjust for Docker).

### Running the Application
1. Build and start the services:
   ```bash
   docker-compose up --build
   ```
2. Access the frontend at http://localhost:8501
3. The backend API is available at http://localhost:8000

### Testing
- Health check: Visit http://localhost:8000/health
- Use the frontend form to generate plans

## Architecture

- **Backend**: FastAPI with local Ollama LLM integration
- **Frontend**: Streamlit with form inputs and plan display
- **Communication**: HTTP via httpx, no direct imports

## Development

To run locally without Docker:
1. Backend: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
2. Frontend: `cd frontend && pip install -r requirements.txt && streamlit run app.py`

## Notes

- All secrets are loaded from environment variables (none required for local Ollama).
- The application uses the local Ollama `llama3.1:8b` model.
- Plans are generated with both constrained and unconstrained versions for comparison.
