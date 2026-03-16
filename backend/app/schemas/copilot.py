"""Pydantic schemas for Compliance Copilot chat."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CopilotMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class CopilotChatRequest(BaseModel):
    session_id: uuid.UUID | None = None
    message: str = Field(..., min_length=1, max_length=4000)


class CopilotChatResponse(BaseModel):
    session_id: uuid.UUID
    response: str
    sources: list[str] = []


class CopilotSessionRead(BaseModel):
    id: uuid.UUID
    user_id: str
    messages: list[dict] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
