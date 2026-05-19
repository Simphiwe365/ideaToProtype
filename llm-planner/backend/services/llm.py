"""LLM service module for generating constrained and unconstrained prototype manufacturing plans 
for local makers in South African workshops/TVET centres using Groq API.

Functions:
- generate_constrained_plan(request: PlanRequest) -> str: Generates a realistic plan respecting tools, materials, 
  budget, and skill constraints. Output: structured plain text with prototype description, 4-6 numbered steps 
  (tools/materials used, cost per step), total time, repair tip, safety note.
- generate_unconstrained_plan(idea: str) -> str: Generates an ideal plan assuming unlimited resources. 
  Same output structure for comparison.

Error handling: Returns 'ERROR: {message}' on API failure.
"""

import os
from typing import List
from dotenv import load_dotenv
from groq import Groq
from models.schemas import PlanRequest

# Change this to swap models across the entire file
GROQ_MODEL = "llama-3.1-8b-instant"

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
if api_key is None:
    raise ValueError("GROQ_API_KEY missing from .env file. Add it as: GROQ_API_KEY=your_actual_key_here (no spaces around =)")

client = Groq(api_key=api_key)


def generate_constrained_plan(request: PlanRequest) -> str:
    try:
<<<<<<< HEAD
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a prototype planning assistant for local makers in informal workshops and TVET centres in South Africa. 
You help turn ideas into buildable prototypes using what's actually available locally.""" 
                },
                {
                    "role": "user",
                    "content": f"""Generate a constrained prototype plan for this product idea:

IDEA: {request.idea}
TOOLS (use ONLY these): {', '.join(request.tools)}
MATERIALS (use ONLY these): {', '.join(request.materials)}  
BUDGET: R{request.budget_zar} maximum total
SKILL LEVEL: {request.skill_level}

OUTPUT EXACTLY in this plain text structure (no markdown, clear labels):

PROTOTYPE DESCRIPTION: [1-2 sentences]

BUILD STEPS:
1. [step using only listed tools/materials] - R[cost] - [time]
2. [step] - R[cost] - [time]
... (4-6 steps total)

TOTAL ESTIMATED TIME: [X hours]
ESTIMATED TOTAL COST: R[X]

REPAIRABILITY TIP: [one tip]
SAFETY NOTE: [one safety note]

Keep costs under budget. Match skill level difficulty."""
                }
            ],
            max_tokens=1024
=======
        # FIX: Pass timeout to ollama.Client() constructor (not to .chat())
        # The ollama library accepts timeout directly in the constructor via BaseClient
        client = ollama.Client(host="http://127.0.0.1:11434", timeout=_timeout)
        response = client.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.7, "num_predict": 200},
>>>>>>> 240ff365a7a1a841a81f890b52eef3926e5a4f36
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"ERROR: {str(e)}"


def generate_unconstrained_plan(idea: str) -> str:
    """Generate an unconstrained manufacturing plan for the product idea."""
    try:
<<<<<<< HEAD
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a prototype planning assistant for local makers in informal workshops and TVET centres in South Africa. 
You help turn ideas into buildable prototypes using what's actually available locally.""" 
                },
                {
                    "role": "user",
                    "content": f"""Generate an IDEAL prototype plan for this product idea (unconstrained - assume access to any common tools, 
materials, and skills):

IDEA: {idea}

OUTPUT EXACTLY in this plain text structure (no markdown, clear labels):

PROTOTYPE DESCRIPTION: [1-2 sentences]

BUILD STEPS:
1. [step] - R[cost] - [time]
2. [step] - R[cost] - [time]
... (4-6 steps total)

TOTAL ESTIMATED TIME: [X hours]
ESTIMATED TOTAL COST: R[X]

REPAIRABILITY TIP: [one tip]
SAFETY NOTE: [one safety note]

Make this the best possible prototype design."""
                }
            ],
            max_tokens=1024
=======
        # FIX: Pass timeout to ollama.Client() constructor (not to .chat())
        # The ollama library accepts timeout directly in the constructor via BaseClient
        client = ollama.Client(host="http://127.0.0.1:11434", timeout=_timeout)
        response = client.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.7, "num_predict": 200},
>>>>>>> 240ff365a7a1a841a81f890b52eef3926e5a4f36
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"ERROR: {str(e)}"

