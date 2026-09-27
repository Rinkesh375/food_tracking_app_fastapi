from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlmodel import Session, select

from database import get_session
from models import Order, OrderStatus


router = APIRouter()

IST = ZoneInfo("Asia/Kolkata")


@router.get(
    "/orders/daily-summary",
    status_code=status.HTTP_200_OK,
)
def daily_summary(
    summary_date: date | None = Query(
        default=None,
        description="Date for summary (YYYY-MM-DD)",
    ),
    session: Session = Depends(get_session),
):
    summary_date = summary_date or datetime.now(IST).date()

    start = datetime.combine(
        summary_date,
        time.min,
        tzinfo=IST,
    )

    end = datetime.combine(
        summary_date + timedelta(days=1),
        time.min,
        tzinfo=IST,
    )

    statement = (
        select(
            Order.status,
            func.count(Order.id).label("count"),
        )
        .where(
            Order.created_at >= start,
            Order.created_at < end,
        )
        .group_by(Order.status)
    )

    results = session.exec(statement).all()
    print(f"Result:{results}")

    summary = {
        order_status.value: 0
        for order_status in OrderStatus
    }
    print(f"summary:{summary}")

    for order_status, count in results:
        summary[order_status.value] = count

    total = sum(summary.values())

    return {
        "date": summary_date.isoformat(),
        "total_orders": total,
        "summary": summary,
    }