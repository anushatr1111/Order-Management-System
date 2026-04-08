"""
models/order_model.py
Pydantic schemas used for request validation, response serialisation,
and internal DB representation.

Separation of concerns:
  - OrderCreate  → what the client sends (POST body)
  - OrderUpdate  → what the client sends when updating status (PUT body)
  - OrderDB      → what we store / return from the service layer
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------
class OrderStatus(str, Enum):
    """Allowed lifecycle states for an order."""
    pending   = "pending"
    confirmed = "confirmed"
    shipped   = "shipped"
    delivered = "delivered"


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------
class OrderCreate(BaseModel):
    """Payload required to create a new order."""
    user_id:     int         = Field(..., gt=0, description="ID of the user placing the order")
    items:       List[str]   = Field(..., min_length=1, description="Non-empty list of item names")
    total_price: float       = Field(..., gt=0, description="Total price; must be greater than 0")

    @field_validator("items")
    @classmethod
    def items_must_not_be_empty_strings(cls, v: List[str]) -> List[str]:
        """Reject lists that contain blank item names."""
        for item in v:
            if not item.strip():
                raise ValueError("Item names must not be empty strings")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 42,
                "items": ["Widget A", "Gadget B"],
                "total_price": 99.99,
            }
        }
    }


class OrderUpdate(BaseModel):
    """Payload required to update an order's status."""
    status: OrderStatus = Field(..., description="New status for the order")

    model_config = {
        "json_schema_extra": {
            "example": {"status": "confirmed"}
        }
    }


# ---------------------------------------------------------------------------
# Response / storage schema
# ---------------------------------------------------------------------------
class OrderDB(BaseModel):
    """Full order representation – stored in the DB and returned to clients."""
    id:          UUID        = Field(default_factory=uuid4)
    user_id:     int
    items:       List[str]
    total_price: float
    status:      OrderStatus = OrderStatus.pending
    created_at:  datetime    = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at:  datetime    = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"from_attributes": True}
