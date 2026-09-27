from fastapi import APIRouter, Depends, HTTPException, Query, status
from database import get_session
from models import Order, OrderCreate, OrderStatus, OrderUpdate, StatusLog
from sqlmodel import Session, select
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")
router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/orders",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session),
) -> Order:

    db_order = Order(**order_data.model_dump())

    try:
        session.add(db_order)
        session.commit()
        session.refresh(db_order)

        return db_order

    except Exception:
        session.rollback()
        raise


@router.get(
    "/orders",
    response_model=list[Order],
    status_code=status.HTTP_200_OK,
)
def list_orders(
    order_status: OrderStatus | None = Query(
        default=None,
        description="Filter by order status",
    ),
    created_date: date | None = Query(
        default=None,
        description="Filter by creation date (YYYY-MM-DD)",
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    session: Session = Depends(get_session),
) -> list[Order]:

    query = select(Order)

    if order_status is not None:
        query = query.where(Order.status == order_status)

    if created_date is not None:
        print(f"created_at:{created_date}")
        start = datetime.combine(created_date, time.min,tzinfo=IST)
        end = datetime.combine(created_date + timedelta(days=1), time.min,tzinfo=IST)

        query = query.where(
            Order.created_at >= start,
            Order.created_at < end,
        )

    query = query.offset(skip).limit(limit)

    return session.exec(query).all()



@router.patch(
    "/orders/{order_id}",
    response_model=Order,
    status_code=status.HTTP_200_OK,
)
def update_order(
    order_id: int,
    update_data: OrderUpdate,
    session: Session = Depends(get_session),
) -> Order:

    db_order = session.get(Order, order_id)

    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    update_values = update_data.model_dump(exclude_unset=True)

    for field, value in update_values.items():
        setattr(db_order, field, value)

    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    return db_order
    