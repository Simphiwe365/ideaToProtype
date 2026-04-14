# LLM-Guided Micro-Manufacturing Planner

A proof-of-concept web application for generating LLM-guided manufacturing plans with separated frontend and backend.

## Project Overview

This application allows local makers to input a product idea and local constraints, receiving an LLM-generated prototype plan. The architecture strictly separates the backend (FastAPI) and frontend (Streamlit).

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Groq API key (sign up at https://groq.com/)

### Environment Setup
1. Clone or download this repository.
2. Navigate to the `llm-planner` directory.
3. In `backend/.env`, replace `your_api_key_here` with your actual Groq API key.
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

- **Backend**: FastAPI with Groq LLM integration
- **Frontend**: Streamlit with form inputs and plan display
- **Communication**: HTTP via httpx, no direct imports

## Development

To run locally without Docker:
1. Backend: `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
2. Frontend: `cd frontend && pip install -r requirements.txt && streamlit run app.py`

## Notes

- All secrets are loaded from environment variables.
- The application uses a configurable Groq model (`GROQ_MODEL`) with a supported default.
- Plans are generated with both constrained and unconstrained versions for comparison.