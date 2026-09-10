"""Factory for creating personal speech memory store instances."""

from typing import Optional
from app.core.config import Settings, settings as default_settings
from app.memory.base import MemoryStore
from app.memory.mock import MockMemoryStore
from app.memory.supabase import SupabaseMemoryStore


def get_memory_store(config: Optional[Settings] = None) -> MemoryStore:
    """Create and return a MemoryStore implementation based on configuration."""
    cfg = config or default_settings

    if not cfg.ENABLE_PERSONAL_MEMORY:
        return MockMemoryStore()

    if cfg.SUPABASE_URL and cfg.SUPABASE_KEY:
        return SupabaseMemoryStore(
            supabase_url=cfg.SUPABASE_URL,
            supabase_key=cfg.SUPABASE_KEY,
        )

    return MockMemoryStore()
