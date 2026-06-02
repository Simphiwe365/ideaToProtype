"""LLM service module for generating constrained and unconstrained prototype manufacturing plans 
for local makers in South African workshops/TVET centres using Groq API.

Functions:
- generate_constrained_plan(request: PlanRequest) -> str: Generates a realistic plan respecting tools, materials, 
  budget, and skill constraints. Output: structured plain text with clear, detailed, beginner-friendly steps.
- generate_unconstrained_plan(idea: str) -> str: Generates an ideal plan assuming unlimited resources. 
  Same output structure for comparison.

Error handling: Returns error message on API failure.
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
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a prototype planning assistant for local makers in informal workshops and TVET centres in South Africa. 
You create CRYSTAL CLEAR, step-by-step instructions that a beginner can easily follow without confusion.
Each step must be so detailed that someone with no experience can build it.""" 
                },
                {
                    "role": "user",
                    "content": f"""Generate a constrained prototype plan for this product idea:

IDEA: {request.idea}
TOOLS (use ONLY these): {', '.join(request.tools)}
MATERIALS (use ONLY these): {', '.join(request.materials)}  
BUDGET: R{request.budget_zar} maximum total
SKILL LEVEL: {request.skill_level}

OUTPUT EXACTLY in this plain text structure (no markdown):

PROTOTYPE DESCRIPTION: [1-2 sentences - what is the final thing?]

REQUIRED TOOLS AND MATERIALS:
- Tool/Material Name (Quantity): Unit Price (R) × Quantity = Total Price (R)
- Example: Hand Drill (1): R150 × 1 = R150
- Example: Wood Sheet 2x4 (2): R200 × 2 = R400
- Example: Saw Blade (1): R50 × 1 = R50
[List ALL tools and materials with quantities and prices. Stay within budget.]

SUBTOTAL FOR MATERIALS & TOOLS: R[total]
REMAINING BUDGET: R[amount left]

BUILD STEPS:
For EACH step, write it like this:
STEP 1: [Clear action verb]. 
  - Tools/Materials needed for this step: [list what from above you'll use]
  - How to do it: [Very detailed explanation - measurements, angles, directions. Write like explaining to someone who has never done this before]
  - Measurement check: [What should it look like when done? Any dimensions to verify?]
  - Safety warning: [Any danger? What to watch out for?]
  - Time needed: [X minutes]

STEP 2: [Next action]
  - Tools/Materials needed for this step: [list specific items]
  - How to do it: [Detailed steps]
  - Measurement check: [Verification]
  - Safety warning: [Cautions]
  - Time needed: [minutes]

[Continue for 4-6 steps total. EVERY step must be extremely clear and easy to follow.]

TOTAL BUILD TIME: [X hours total]
TOTAL COST: R[amount within budget]

REPAIRABILITY: [One specific tip for fixing it later]
SAFETY SUMMARY: [Overall safety reminder]

Make each step so clear that anyone can follow it without asking questions."""
                }
            ],
            max_tokens=2048
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"ERROR: {str(e)}"


def generate_unconstrained_plan(idea: str) -> str:
    """Generate an unconstrained manufacturing plan for the product idea with crystal-clear steps."""
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a prototype planning assistant for local makers in informal workshops and TVET centres in South Africa. 
You create CRYSTAL CLEAR, step-by-step instructions that a beginner can easily follow without confusion.
Each step must be so detailed that someone with no experience can build it.""" 
                },
                {
                    "role": "user",
                    "content": f"""Generate an IDEAL prototype plan for this product idea (unconstrained - assume access to any common tools, 
materials, and skills). Make it the BEST possible design and build process.

IDEA: {idea}

OUTPUT EXACTLY in this plain text structure (no markdown, VERY DETAILED STEPS):

PROTOTYPE DESCRIPTION: [1-2 sentences - what is the final thing?]

REQUIRED TOOLS AND MATERIALS:
- Tool/Material Name (Quantity): Unit Price (R) × Quantity = Total Price (R)
- Example: Professional Power Drill (1): R800 × 1 = R800
- Example: Premium Wood Sheet (3): R400 × 3 = R1200
- Example: Precision Saw Blade (1): R150 × 1 = R150
[List ALL tools and materials with quantities and prices. Choose premium quality options.]

SUBTOTAL FOR MATERIALS & TOOLS: R[total]

BUILD STEPS:
For EACH step, write it like this:
STEP 1: [Clear action verb]. 
  - Tools/Materials needed for this step: [list what from above you'll use]
  - How to do it: [Very detailed explanation - measurements, angles, directions. Write like explaining to someone who has never done this before]
  - Measurement check: [What should it look like when done? Any dimensions to verify?]
  - Best practice tip: [Pro tip for best quality]
  - Time needed: [X minutes]

STEP 2: [Next action]
  - Tools/Materials needed for this step: [list specific items]
  - How to do it: [Detailed steps]
  - Measurement check: [Verification]
  - Best practice tip: [Pro tip]
  - Time needed: [minutes]

[Continue for 4-6 steps total. EVERY step must be extremely clear and easy to follow.]

TOTAL BUILD TIME: [X hours total]
TOTAL COST: R[amount]

MAINTENANCE: [Specific maintenance tips]
QUALITY NOTES: [How to ensure high quality]

Make each step so clear that anyone can follow it without asking questions."""
                }
            ],
            max_tokens=2048
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"ERROR: {str(e)}"



