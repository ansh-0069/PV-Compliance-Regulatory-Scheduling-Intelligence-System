"""Compliance Copilot Service.

LangChain-powered conversational assistant that answers questions about
submissions, CAPAs, and compliance metrics using natural-language queries.

In production this connects to the OpenAI/Claude API. For development,
a stub response is returned when the API key is not configured.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import EntityNotFoundError
from app.models.capa import CAPA
from app.models.copilot import CopilotSession
from app.models.submission import Submission
from app.models.user import User
from app.schemas.copilot import CopilotChatRequest, CopilotChatResponse


async def _build_system_context(db: AsyncSession) -> str:
    """Build a system prompt enriched with live database metrics."""
    total_subs = (await db.execute(select(func.count(Submission.id)))).scalar() or 0
    overdue_subs = (await db.execute(
        select(func.count(Submission.id)).where(Submission.status == "Overdue")
    )).scalar() or 0
    open_capas = (await db.execute(
        select(func.count(CAPA.id)).where(CAPA.status != "Closed")
    )).scalar() or 0

    return (
        "You are the PV Compliance Copilot, an expert assistant for pharmacovigilance operations.\n"
        "You help users understand submission schedules, CAPA statuses, and audit readiness.\n\n"
        f"Current system metrics:\n"
        f"- Total submissions: {total_subs}\n"
        f"- Overdue submissions: {overdue_subs}\n"
        f"- Open CAPAs: {open_capas}\n\n"
        "Answer concisely and professionally. Cite relevant data when possible."
    )


async def _call_llm(system_prompt: str, messages: list[dict]) -> str:
    """Call the LLM API via LangChain or return a stub in dev."""
    if settings.OPENAI_API_KEY.startswith("sk-your"):
        # Stub response for development without a real API key
        return (
            "I'm the PV Compliance Copilot. I can help you with submission schedules, "
            "CAPA management, and audit readiness metrics. "
            "Please configure a valid OPENAI_API_KEY for full AI-powered responses."
        )

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

        llm = ChatOpenAI(model=settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)

        lc_messages = [SystemMessage(content=system_prompt)]
        for msg in messages:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))

        response = await llm.ainvoke(lc_messages)
        return response.content
    except Exception as e:
        return f"Copilot is temporarily unavailable: {str(e)}"


async def get_copilot_response(
    db: AsyncSession,
    user: User,
    request: CopilotChatRequest,
) -> CopilotChatResponse:
    """Process a copilot chat message: load/create session, call LLM, persist."""

    # Load or create session
    if request.session_id:
        result = await db.execute(
            select(CopilotSession).where(CopilotSession.id == request.session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise EntityNotFoundError("CopilotSession", str(request.session_id))
    else:
        session = CopilotSession(user_id=str(user.id), messages=[])
        db.add(session)
        await db.flush()
        await db.refresh(session)

    # Append user message
    messages = list(session.messages or [])
    messages.append({"role": "user", "content": request.message})

    # Build context and call LLM
    system_prompt = await _build_system_context(db)
    ai_response = await _call_llm(system_prompt, messages)

    # Append assistant response
    messages.append({"role": "assistant", "content": ai_response})
    session.messages = messages
    await db.flush()

    return CopilotChatResponse(
        session_id=session.id,
        response=ai_response,
        sources=["submissions", "capas", "audit_scores"],
    )


async def get_session(db: AsyncSession, session_id: uuid.UUID) -> CopilotSession:
    """Retrieve a copilot session by ID."""
    result = await db.execute(
        select(CopilotSession).where(CopilotSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise EntityNotFoundError("CopilotSession", str(session_id))
    return session
