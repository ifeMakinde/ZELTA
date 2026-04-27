from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CopilotMessage(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class CopilotRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    question: str = Field(..., min_length=1, max_length=1000)
    conversation_history: List[CopilotMessage] = Field(default_factory=list)


class ContextPill(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    label: str
    value: str


class CopilotResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    answer: str
    verdict: Optional[str] = None  # SAVE / INVEST / HOLD
    verdict_amount: Optional[float] = None
    context_pills: List[ContextPill] = Field(default_factory=list)
    confidence: float
    sources: List[str] = Field(default_factory=list)


class CopilotAPIResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    success: bool
    data: CopilotResponse
