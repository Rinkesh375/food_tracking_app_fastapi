from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_table
from routes.orders import router as orders_router
from routes.stats import router as stats_router


@asynccontextmanager
async def lifespan(app:FastAPI):
    create_table()
    print("Database tables created.")
    yield
    print("Application shutdown")
    
    
app = FastAPI(
    title="Dabbawala Delivery API",
    description="API for managing food tracking order statuses.",
    version="1.0.0",
    lifespan=lifespan
)    

app.include_router(orders_router)
app.include_router(stats_router)