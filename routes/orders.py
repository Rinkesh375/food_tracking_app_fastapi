from fastapi import APIRouter, Depends, HTTPException, Query, status
from database import get_session
from models import Order, OrderCreate, OrderStatus, OrderUpdate, StatusLog
from sqlmodel import Session, select
from datetime import datetime, date, time

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


@router.get("/orders", response_model=list[Order], status_code=status.HTTP_200_OK)
def list_orders(
    status: OrderStatus | None = Query(
        default=None, description="Filter by order status"
    ),
    created_date: str | None = Query(
        default=None, description="Filter by creation date (YYYY-MM-DD)"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> list[Order]:

    query = select(Order)

    if status:
        query = query.where(OrderStatus == status)

    if created_date:
        created_date = datetime.strptime(created_date, "%Y-%m-%d").date()
        start = datetime.combine(created_date, time.min)
        end = datetime.combine(created_date, time.max)
        query = query.where(Order.created_at >= start, Order.created_at <= end)
        
    query = query.offset(skip).limit(limit) 
    
    return session.exec(query).all()
   
