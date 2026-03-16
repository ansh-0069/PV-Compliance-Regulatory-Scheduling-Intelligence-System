"""QC Engine Service.

Handles file upload to MinIO and enqueues the Celery QC analysis task.
"""

import uuid

from fastapi import UploadFile
from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.qc import QCCheck
from app.schemas.qc import QCCheckUploadResponse


def _get_minio_client() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.MINIO_SECURE,
    )


async def upload_and_enqueue_qc(
    db: AsyncSession,
    submission_id: uuid.UUID,
    file: UploadFile,
) -> QCCheckUploadResponse:
    """Upload report file to MinIO and create a pending QC check.

    Steps:
    1. Upload the file to the MinIO bucket under a unique key.
    2. Create a QCCheck row in status=Pending.
    3. (In production) Enqueue a Celery task for async analysis.
    4. Return the tracking ID immediately.
    """
    client = _get_minio_client()

    # Ensure bucket exists
    if not client.bucket_exists(settings.MINIO_BUCKET):
        client.make_bucket(settings.MINIO_BUCKET)

    # Upload file
    file_key = f"qc/{submission_id}/{uuid.uuid4()}/{file.filename}"
    contents = await file.read()

    from io import BytesIO
    client.put_object(
        settings.MINIO_BUCKET,
        file_key,
        BytesIO(contents),
        len(contents),
        content_type=file.content_type or "application/octet-stream",
    )

    # Persist QC check record
    qc_check = QCCheck(
        submission_id=submission_id,
        file_key=file_key,
        status="Pending",
    )
    db.add(qc_check)
    await db.flush()
    await db.refresh(qc_check)

    # Enqueue Celery task (import here to avoid circular deps)
    try:
        from app.tasks.qc_tasks import run_qc_analysis
        run_qc_analysis.delay(str(qc_check.id))
    except Exception:
        pass  # Celery may not always be available in dev

    return QCCheckUploadResponse(qc_check_id=qc_check.id)
