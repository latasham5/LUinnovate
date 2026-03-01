"""
Supabase Client — database query helpers.

Used by Developer 3 for all logging, flag history, scorecards, and analytics.
"""

from config.supabase import supabase
from typing import Optional


async def insert_record(table: str, data: dict) -> dict:
    """Insert a record into a Supabase table."""
    result = supabase.table(table).insert(data).execute()
    return result.data[0] if result.data else {}


async def query_records(
    table: str,
    filters: dict = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    order_by: str = "created_at",
    ascending: bool = False,
    limit: int = 100,
) -> list[dict]:
    """Query records from a Supabase table with optional filters."""
    query = supabase.table(table).select("*")

    if filters:
        for key, value in filters.items():
            query = query.eq(key, value)

    if date_from:
        query = query.gte("created_at", date_from)

    if date_to:
        query = query.lte("created_at", date_to)

    query = query.order(order_by, desc=not ascending).limit(limit)
    result = query.execute()

    return result.data if result.data else []


async def count_records(table: str, filters: dict = None) -> int:
    """Count records matching filters."""
    query = supabase.table(table).select("*", count="exact")

    if filters:
        for key, value in filters.items():
            query = query.eq(key, value)

    result = query.execute()
    return result.count if result.count else 0


async def update_record(table: str, record_id: str, data: dict, id_column: str = "id") -> dict:
    """Update a record in a Supabase table."""
    result = supabase.table(table).update(data).eq(id_column, record_id).execute()
    return result.data[0] if result.data else {}


async def delete_records(table: str, filters: dict) -> int:
    """Delete records matching filters. Returns count of deleted records."""
    query = supabase.table(table).delete()

    for key, value in filters.items():
        query = query.eq(key, value)

    result = query.execute()
    return len(result.data) if result.data else 0
