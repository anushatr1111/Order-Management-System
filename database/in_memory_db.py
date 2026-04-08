"""
database/in_memory_db.py
In-memory database using a plain Python dict.
Swap this module for a real DB adapter (SQLAlchemy, Motor, etc.) without
touching any other layer – that is the point of clean architecture.
"""

from typing import Dict
from uuid import UUID


# ---------------------------------------------------------------------------
# Singleton in-memory store
# Key   : Order UUID
# Value : dict representation of the order (mirrors OrderDB schema)
# ---------------------------------------------------------------------------
_orders: Dict[UUID, dict] = {}


def get_db() -> Dict[UUID, dict]:
    """
    FastAPI dependency – yields the shared in-memory orders store.
    Usage:
        db: Dict = Depends(get_db)
    """
    return _orders
