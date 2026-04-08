"""
routes/order_routes.py
HTTP layer only – no business logic lives here.

Each route:
  1. Declares its contract (path, method, status code, response model)
  2. Receives dependencies via FastAPI's Depends()
  3. Delegates all work to OrderService
  4. Returns the service result (FastAPI serialises it via response_model)
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status

from database.in_memory_db import get_db
from models.order_model import OrderCreate, OrderDB, OrderStatus, OrderUpdate
from services.order_service import OrderService

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency: build an OrderService scoped to the current request
# ---------------------------------------------------------------------------
def get_order_service(db=Depends(get_db)) -> OrderService:
    """
    Dependency factory.
    FastAPI calls get_db() first, then passes its result into get_order_service().
    Swap get_db for any other DB provider and nothing else changes.
    """
    return OrderService(db)


# ---------------------------------------------------------------------------
# POST /orders  – Create a new order
# ---------------------------------------------------------------------------
@router.post(
    "/",
    response_model=OrderDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
)
async def create_order(
    payload: OrderCreate,
    service: OrderService = Depends(get_order_service),
) -> OrderDB:
    """
    Create an order with the provided items and total price.
    The new order is automatically assigned *pending* status.
    """
    logger.info("POST /orders – user_id=%s", payload.user_id)
    return await service.create_order(payload)


# ---------------------------------------------------------------------------
# GET /orders  – List all orders (with optional status filter)
# ---------------------------------------------------------------------------
@router.get(
    "/",
    response_model=List[OrderDB],
    status_code=status.HTTP_200_OK,
    summary="List all orders",
)
async def get_all_orders(
    status: Optional[OrderStatus] = None,   # ?status=delivered
    service: OrderService = Depends(get_order_service),
) -> List[OrderDB]:
    """
    Retrieve all orders.
    Use the optional **status** query parameter to filter results,
    e.g. `GET /orders?status=shipped`.
    """
    logger.info("GET /orders – status_filter=%s", status)
    return await service.get_all_orders(status_filter=status)


# ---------------------------------------------------------------------------
# GET /orders/{order_id}  – Fetch a single order
# ---------------------------------------------------------------------------
@router.get(
    "/{order_id}",
    response_model=OrderDB,
    status_code=status.HTTP_200_OK,
    summary="Get order by ID",
)
async def get_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> OrderDB:
    """Retrieve a single order by its UUID. Returns 404 if not found."""
    logger.info("GET /orders/%s", order_id)
    return await service.get_order(order_id)


# ---------------------------------------------------------------------------
# PUT /orders/{order_id}  – Update order status
# ---------------------------------------------------------------------------
@router.put(
    "/{order_id}",
    response_model=OrderDB,
    status_code=status.HTTP_200_OK,
    summary="Update order status",
)
async def update_order_status(
    order_id: UUID,
    payload: OrderUpdate,
    service: OrderService = Depends(get_order_service),
) -> OrderDB:
    """
    Update the **status** of an existing order.
    Returns 404 if the order doesn't exist.
    Returns 400 if the new status equals the current one.
    """
    logger.info("PUT /orders/%s – new_status=%s", order_id, payload.status)
    return await service.update_order_status(order_id, payload)


# ---------------------------------------------------------------------------
# DELETE /orders/{order_id}  – Remove an order
# ---------------------------------------------------------------------------
@router.delete(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an order",
)
async def delete_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
) -> dict:
    """Permanently remove an order. Returns 404 if not found."""
    logger.info("DELETE /orders/%s", order_id)
    return await service.delete_order(order_id)
