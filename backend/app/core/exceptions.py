"""Custom exception classes and FastAPI exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class PVBaseException(Exception):
    """Base exception for PV Compliance system."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class EntityNotFoundError(PVBaseException):
    def __init__(self, entity: str, entity_id: str):
        super().__init__(f"{entity} '{entity_id}' not found", status_code=404)


class InvalidStateTransitionError(PVBaseException):
    def __init__(self, current: str, target: str):
        super().__init__(
            f"Invalid state transition: {current} → {target}", status_code=422
        )


class QCCheckInProgressError(PVBaseException):
    def __init__(self):
        super().__init__("A QC check is already in progress for this submission", status_code=409)


def register_exception_handlers(app: FastAPI):
    """Register custom exception handlers on the FastAPI app."""

    @app.exception_handler(PVBaseException)
    async def pv_exception_handler(_request: Request, exc: PVBaseException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )
