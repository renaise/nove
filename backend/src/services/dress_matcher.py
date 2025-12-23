"""Dress matching service - queries dresses by silhouette and size."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import Dress


async def get_matching_dresses(
    session: AsyncSession,
    silhouettes: list[str],
    user_size: int,
    *,
    price_min_cents: int | None = None,
    price_max_cents: int | None = None,
    limit: int = 10,
) -> tuple[list[Dress], int]:
    """
    Get dresses matching silhouettes AND available in user's size.

    Args:
        session: Database session
        silhouettes: List of silhouette types to match
        user_size: User's calculated dress size
        price_min_cents: Optional minimum price filter (in cents)
        price_max_cents: Optional maximum price filter (in cents)
        limit: Maximum results to return

    Returns:
        Tuple of (list of matching dresses, total count)
    """
    # Build base query
    query = select(Dress).where(
        Dress.silhouette.in_(silhouettes),
        Dress.size_min <= user_size,
        Dress.size_max >= user_size,
    )

    # Apply price filters
    if price_min_cents is not None:
        query = query.where(Dress.price_cents >= price_min_cents)
    if price_max_cents is not None:
        query = query.where(Dress.price_cents <= price_max_cents)

    # Get total count (for pagination info)
    count_query = select(Dress.id).where(
        Dress.silhouette.in_(silhouettes),
        Dress.size_min <= user_size,
        Dress.size_max >= user_size,
    )
    if price_min_cents is not None:
        count_query = count_query.where(Dress.price_cents >= price_min_cents)
    if price_max_cents is not None:
        count_query = count_query.where(Dress.price_cents <= price_max_cents)

    count_result = await session.execute(count_query)
    total_count = len(count_result.all())

    # Order by price and apply limit
    query = query.order_by(Dress.price_cents).limit(limit)

    result = await session.execute(query)
    dresses = list(result.scalars().all())

    return dresses, total_count


async def get_dress_by_id(session: AsyncSession, dress_id: str) -> Dress | None:
    """Get a single dress by ID."""
    result = await session.execute(select(Dress).where(Dress.id == dress_id))
    return result.scalar_one_or_none()


async def get_dresses_by_silhouette(
    session: AsyncSession,
    silhouette: str,
    *,
    limit: int = 20,
) -> list[Dress]:
    """Get dresses for a specific silhouette type."""
    query = (
        select(Dress).where(Dress.silhouette == silhouette).order_by(Dress.price_cents).limit(limit)
    )
    result = await session.execute(query)
    return list(result.scalars().all())
