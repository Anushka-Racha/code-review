from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
import json
import re
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CodeRefine API", description="AI-Powered Code Reviewer & Optimizer")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str

class AnalysisResult(BaseModel):
    score: int
    issues: List[str]
    optimizations: List[str]
    security_concerns: List[str]
    complexity: str
    improved_code: str
    explanation: str
    mode: str

def generate_demo_result(code: str) -> dict:
    """Generate a dynamic demo response based on input code."""
    lines = code.strip().split('\n')
    issues = []
    optimizations = []
    complexity = "O(n)"
    score = 85
    improved_code = code.strip()
    explanation = "Demo mode: Basic improvements applied."
    
    # Heuristic 1: Fix range(len()) pattern
    if "for " in code and "range(len(" in code:
        issues.append("Avoid using range(len()) pattern, use direct iteration.")
        optimizations.append("Use enumerate() or iterate directly over the collection.")
        complexity = "O(n^2)"
        score -= 15
        # Simple transformation (very basic)
        improved_code = code.strip().replace("range(len(", "enumerate(")
        explanation = "Replaced range(len()) with enumerate() for better performance."
        
    # Heuristic 2: Fix None checks
    elif "==" in code and "None" in code:
        issues.append("Use 'is None' for None checks.")
        optimizations.append("Use identity check 'is None' instead of equality '== None'.")
        score -= 5
        improved_code = code.strip().replace("== None", "is None")
        explanation = "Fixed None comparison to use 'is None'."
        
    # Heuristic 3: Check for inefficient list operations
    elif "append" in code and "for" in code:
        issues.append("Consider using list comprehension for better performance.")
        optimizations.append("List comprehensions are generally faster than explicit loops.")
        score -= 10
        explanation = "Consider refactoring to list comprehension."
        
    # Default if no specific pattern matched
    else:
        issues.append("Code looks reasonably clean.")
        optimizations.append("Consider adding type hints for better readability.")
        complexity = "O(1)"
        score = 95
        
    return {
        "score": max(0, min(100, score)),
        "issues": issues,
        "optimizations": optimizations if optimizations else ["None found"],
        "security_concerns": ["None found"],
        "complexity": complexity,
        "improved_code": improved_code,
        "explanation": explanation,
        "mode": "demo"
    }

def generate_prompt(code: str) -> str:
    return f"""
You are an expert Python code reviewer. Analyze the following code and provide a JSON response.

INSTRUCTIONS:
- Identify specific issues in the code (e.g., inefficient loops, bad variable names, redundant logic).
- Provide concrete optimization suggestions specific to this code.
- Write the IMPROVED version of the code that fixes these issues.
- Give an explanation of what was changed and why.

The response MUST be valid JSON with these exact keys:
1. "score": integer (0-100) - Rate readability, efficiency, security.
2. "issues": list of strings - Specific issues found in THIS code.
3. "optimizations": list of strings - Specific suggestions for THIS code.
4. "security_concerns": list of strings - Security risks in THIS code.
5. "complexity": string - Time and space complexity.
6. "improved_code": string - ONLY the raw improved code, NO markdown fences.
7. "explanation": string - Brief summary of changes.

CODE TO ANALYZE:
{code}
"""

def query_gemini(prompt: str) -> Optional[dict]:
    """Queries Google Gemini API."""
    try:
        import google.generativeai as genai
        
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment")
            return None
            
        genai.configure(api_key=api_key)
        
        # Use gemini-1.5-flash for faster response
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                logger.warning(f"Failed to parse Gemini JSON response")
                return None
        return None
        
    except Exception as e:
        logger.warning(f"Gemini API failed: {e}")
        return None

@app.get("/api/status")
def get_status():
    """Check which AI backend is available."""
    gemini_result = query_gemini("hello")
    return {
        "status": "ok",
        "mode": "gemini" if gemini_result else "demo",
        "message": "Gemini connected" if gemini_result else "Using Demo Mode (No AI detected)"
    }

@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_code(data: CodeInput):
    # 1. Try Gemini API
    logger.info("Analyzing code with Gemini...")
    gemini_result = query_gemini(generate_prompt(data.code))
    
    if gemini_result:
        gemini_result["mode"] = "gemini"
        return gemini_result
    
    # 2. Fallback to Demo Mode (Dynamic)
    logger.info("Using Demo Mode")
    return generate_demo_result(data.code)

# Note: Frontend runs on port 5173 (Vite), Backend runs on port 8000 (FastAPI)
# API Proxy in Vite co