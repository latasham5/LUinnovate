"""
Supabase client initialization.
"""

from supabase import create_client, Client
from config.settings import settings


def get_supabase_client() -> Client:
    """Create and return a Supabase client instance."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


# Singleton client instance
supabase: Client = get_supabase_client()
