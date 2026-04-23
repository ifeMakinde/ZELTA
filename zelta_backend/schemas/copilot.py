from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CopilotMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class CopilotRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    conversation_history: Optional[List[CopilotMessage]] = []


class ContextPill(BaseModel):
    label: str
    value: str


class CopilotResponse(BaseModel):
    answer: str
    verdict: Optional[str] = None  # SAVE / INVEST / HOLD
    verdict_amount: Optional[float] = None
    context_pills: List[ContextPill]
    confidence: float
    sources: List[str]


class CopilotAPIResponse(BaseModel):
    success: bool
    data: CopilotResponse