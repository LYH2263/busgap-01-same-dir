from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.router import api_router
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.services.seed import seed_if_empty, upgrade_seed_data


def ensure_direction_columns() -> None:
    """旧库可能在引入上下行分向之前建表，补齐 lines/trips 的 direction 列。

    历史数据保持 NULL：判定时按上行兼容，不改变既有阈值字段含义。
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        if "lines" in existing_tables:
            cols = {c["name"] for c in inspector.get_columns("lines")}
            if "direction" not in cols:
                conn.execute(text("ALTER TABLE lines ADD COLUMN direction VARCHAR(8)"))
        if "trips" in existing_tables:
            cols = {c["name"] for c in inspector.get_columns("trips")}
            if "direction" not in cols:
                conn.execute(text("ALTER TABLE trips ADD COLUMN direction VARCHAR(8)"))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_direction_columns()
    if settings.seed_on_empty:
        db = SessionLocal()
        try:
            seed_if_empty(db)
            upgrade_seed_data(db)
        finally:
            db.close()
    yield


app = FastAPI(title="BusGap", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api")
