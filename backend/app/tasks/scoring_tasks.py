"""Audit scoring Celery task.

Triggered daily by Celery Beat to recalculate organisation-wide
audit readiness scores.
"""

from app.tasks.celery_app import celery


@celery.task(name="app.tasks.scoring_tasks.recalculate_all_scores")
def recalculate_all_scores():
    """Recalculate audit scores for all products and the org-wide aggregate.

    Runs daily at 02:00 UTC via Celery Beat.
    """
    import asyncio
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from app.config import settings
    from app.models.product import Product
    from app.services.audit_scorer import recalculate_audit_score

    async def _run():
        engine = create_async_engine(settings.DATABASE_URL)
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        scored_count = 0
        async with session_factory() as db:
            # Per-product scores
            products = (await db.execute(select(Product))).scalars().all()
            for product in products:
                await recalculate_audit_score(db, product.id)
                scored_count += 1

            # Org-wide score
            await recalculate_audit_score(db, None)
            scored_count += 1
            await db.commit()

        await engine.dispose()
        return {"products_scored": scored_count}

    return asyncio.run(_run())
