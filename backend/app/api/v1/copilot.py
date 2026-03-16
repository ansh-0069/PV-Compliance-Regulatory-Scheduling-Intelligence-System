"""Compliance Copilot chat endpoint."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.copilot import CopilotChatRequest, CopilotChatResponse, CopilotSessionRead
from app.services.copilot_chain import get_copilot_response, get_session

router = APIRouter(prefix="/copilot", tags=["Compliance Copilot"])


@router.post("/chat", response_model=CopilotChatResponse)
async def chat(
    body: CopilotChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a natural-language query to the Compliance Copilot.

    The copilot can answer questions about:
    - Submission schedules and deadlines
    - CAPA status and trends
    - Audit readiness metrics
    - Regulatory compliance guidance
    """
    return await get_copilot_response(db, current_user, body)


@router.get("/sessions/{session_id}", response_model=CopilotSessionRead)
async def get_copilot_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Retrieve a past copilot conversation session."""
    return await get_session(db, session_id)
