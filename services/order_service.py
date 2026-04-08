"""
services/order_service.py
Pure business logic – no knowledge of HTTP, request objects, or responses.
All methods are async so they can be awaited inside FastAPI route handlers.

If you later add a real database with async I/O (e.g., asyncpg, Motor),
only this file needs to change.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from models.order_model import OrderCreate, OrderDB, OrderStatus, OrderUpdate

logger = logging.getLogger(__name__)


class OrderService:
    """
    Encapsulates all order-related operations.
    Receives the DB store via dependency injection (constructor injection).
    """

    def __init__(self, db: Dict[UUID, dict]):
        # The in-memory dict acts as our "session" / "connection"
        self._db = db

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------
    async def create_order(self, payload: OrderCreate) -> OrderDB:
        """Persist a new order and return the full OrderDB record."""
        order = OrderDB(
            id=uuid4(),
            user_id=payload.user_id,
            items=payload.items,
            total_price=payload.total_price,
            status=OrderStatus.pending,
        )
        self._db[order.id] = order.model_dump()
        logger.info("Created order %s for user %s", order.id, order.user_id)
        return order

    # ------------------------------------------------------------------
    # READ – single
    # ------------------------------------------------------------------
    async def get_order(self, order_id: UUID) -> OrderDB:
        """Fetch a single order by UUID; raise 404 if not found."""
        raw = self._db.get(order_id)
        if raw is None:
            logger.warning("Order %s not found", order_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id '{order_id}' not found",
            )
        return OrderDB(**raw)

    # ------------------------------------------------------------------
    # READ – collection (with optional status filter)
    # ------------------------------------------------------------------
    async def get_all_orders(
        self, status_filter: Optional[OrderStatus] = None
    ) -> List[OrderDB]:
        """
        Return all orders.
        Optionally filter by status (e.g., ?status=delivered).
        """
        orders = [OrderDB(**raw) for raw in self._db.values()]

        if status_filter is not None:
            orders = [o for o in orders if o.status == status_filter]
            logger.info(
                "Fetched %d orders with status filter '%s'",
                len(orders), status_filter.value,
            )
        else:
            logger.info("Fetched all %d orders", len(orders))

        return orders

    # ------------------------------------------------------------------
    # UPDATE – status only
    # ------------------------------------------------------------------
    async def update_order_status(
        self, order_id: UUID, payload: OrderUpdate
    ) -> OrderDB:
        """
        Update the status of an existing order.
        Raises 404 if the order does not exist.
        Raises 400 if the transition is a no-op (same status).
        """
        raw = self._db.get(order_id)
        if raw is None:
            logger.warning("Update failed – order %s not found", order_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id '{order_id}' not found",
            )

        current_status = raw["status"]
        if current_status == payload.status.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order is already in '{payload.status.value}' status",
            )

        raw["status"]     = payload.status.value
        raw["updated_at"] = datetime.now(timezone.utc)
        self._db[order_id] = raw

        logger.info(
            "Order %s status updated: %s → %s",
            order_id, current_status, payload.status.value,
        )
        return OrderDB(**raw)

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------
    async def delete_order(self, order_id: UUID) -> dict:
        """Remove an order; raise 404 if it doesn't exist."""
        if order_id not in self._db:
            logger.warning("Delete failed – order %s not found", order_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id '{order_id}' not found",
            )
        del self._db[order_id]
        logger.info("Deleted order %s", order_id)
        return {"detail": f"Order '{order_id}' deleted successfully"}
