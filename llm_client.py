# llm_client.py

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

SYSTEM_PROMPT = """
You are a clinical documentation specialist.

Generate a comprehensive clinical summary using clear markdown formatting.

Input:
You will receive a JSON array of clinical facts with statements, sources, and dates.

Output Format:
Use this exact structure with markdown headers:

## 📋 Clinical Summary
[Write a 2-3 paragraph narrative overview synthesizing the key clinical information]

## 🏥 Diagnoses
- [Each diagnosis with relevant details and citation from source]

## 💊 Medications
- [Each medication with dosage, frequency, and citation]

## 📈 Vital Signs
- [Recent vital signs with values, dates, and citations]

## 🩹 Wounds and Skin Assessment
- [Wound descriptions, locations, measurements with citations]

## 🚶 Functional Status
- [Functional assessments, mobility, ADLs with citations]

## 📝 Recent Clinical Notes
- [Key points from recent documentation with dates and citations]

Instructions:
- Include citations referencing the source facts (e.g., "per admission assessment 2024-01-15")
- Use bullet points for clarity
- Include specific dates, values, and measurements when available
- Keep language professional but readable
- Organize information chronologically within each section when relevant
"""

def call_llm(summary):
    """
    Generate clinical summary from structured facts.
    
    Args:
        summary: List of clinical fact dictionaries
        
    Returns:
        str: Markdown-formatted clinical summary
    """
    user_prompt = json.dumps(summary, indent=2)
    
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-small-3.1-24b-instruct:free", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Clinical facts:\n\n{user_prompt}"}
            ],
            temperature=0.3,
            max_tokens=2500
        )
        
        content = response.choices[0].message.content
        
        if content is None:
            raise ValueError("LLM returned empty response")
        
        return content.strip()
        
    except Exception as e:
        print(f"Error calling LLM: {e}")
        raise