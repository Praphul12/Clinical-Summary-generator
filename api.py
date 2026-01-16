# api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_client import call_llm
from typing import List, Dict, Any

app = FastAPI(
    title="Clinical Summary LLM API",
    description="API endpoint for generating clinical summaries using LLM",
    version="1.0.0"
)


# Request/Response models
class ClinicalFactsRequest(BaseModel):
    clinical_facts: List[Dict[str, Any]]


class SummaryResponse(BaseModel):
    summary_markdown: str


# API Endpoint
@app.get("/")
def read_root():
    return {
        "message": "Clinical Summary LLM API",
        "endpoint": "POST /generate-summary"
    }


@app.post("/generate-summary", response_model=SummaryResponse)
def generate_summary(request: ClinicalFactsRequest):
    """
    Generate clinical summary from structured clinical facts using LLM.
    
    Args:
        request: JSON body containing clinical_facts array
        
    Returns:
        Markdown-formatted clinical summary
    """
    try:
        if not request.clinical_facts:
            raise HTTPException(status_code=400, detail="clinical_facts cannot be empty")
        
        
        markdown_summary = call_llm(request.clinical_facts) # generate summary
        
        return SummaryResponse(summary_markdown=markdown_summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)