from __future__ import annotations

from fastapi import FastAPI
from src.users.router import router as users_router
from src.db.session import create_db_and_tables
from src.db import models
from src.cars.router import router as cars_router
from src.trips.router import router as trips_router
from src.routePoints.router import router as routepoints_router
from src.booking.router import router as bookings_router
from src.payments.router import router as payments_router
from src.reviews.router import router as reviews_router
from src.errors.customErrors import register_error_handlers
from src.auth.routes import auth_router
from fastapi.security import HTTPBearer

security = HTTPBearer()

app = FastAPI(
    title="TaxiSystem",
    swagger_ui_init_oauth=None
)

@app.on_event("startup")
async def on_startup() -> None:
    await create_db_and_tables()


@app.get("/health")
async def health():
    return {"status": "ok"}



register_error_handlers(app)
app.include_router(users_router)
app.include_router(cars_router)
app.include_router(trips_router)
app.include_router(routepoints_router)
app.include_router(bookings_router)
app.include_router(payments_router)
app.include_router(reviews_router)
app.include_router(auth_router)