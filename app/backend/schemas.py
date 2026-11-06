from typing import List, Optional
from pydantic import BaseModel, Field

class ContentRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    platform: str
    tone: str = "professional"
    audience: str = "general audience"
    content_type: str = "ideas"  
    use_rag: bool = True
    num_recommendations: int = Field(default=3, ge=1, le=10) # NEW FIELD

class ContentResponse(BaseModel):
    content: str
    platform: str
    topic: str
    rag_used: bool
    model: str

class HealthResponse(BaseModel):
    status: str
    llm_ready: bool
    rag_chunks: int