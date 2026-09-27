from datetime import datetime, timedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.models import Arrival, Line, Trip

STOPS = ["起点站", "市民中心", "火车站", "终点站"]

# (班次, 车牌, 相对发车偏移分钟, 方向)；None 表示历史班次未标方向，按上行兼容
SEED_SPECS = [
    ("T01", "粤A1001", 0, None),
    ("T02", "粤A1002", 2, None),
    ("T03", "粤A1003", 18, None),
    ("T04", "粤A1004", 26, None),
    ("T05", "粤A1005", -5, "down"),
    ("T06", "粤A1006", -3, "down"),
]

def _create_trip(db: Session, line: Line, base: datetime,
                 trip_no: str, vehicle: str, offset: int, direction: str | None) -> None:
    trip = Trip(line_id=line.id, trip_no=trip_no,
                planned_depart=base + timedelta(minutes=offset),
                vehicle_no=vehicle, direction=direction)
    db.add(trip); db.flush()
    for seq, stop in enumerate(STOPS):
        # 上行沿站序每站 6 分钟；下行由终点站反向折回
        stop_offset = seq * 6 if direction != "down" else (len(STOPS) - 1 - seq) * 6
        arrive = base + timedelta(minutes=offset + stop_offset)
        if direction != "down":
            if stop == "市民中心" and trip_no == "T02":
                arrive = base + timedelta(minutes=8)
            if stop == "火车站" and trip_no == "T03":
                arrive = base + timedelta(minutes=30)
        db.add(Arrival(trip_id=trip.id, stop_name=stop, stop_seq=seq, actual_arrive=arrive))

def seed_if_empty(db: Session) -> None:
    if (db.scalar(select(func.count()).select_from(Line)) or 0) > 0:
        return
    base = datetime(2026, 9, 17, 7, 0, 0)
    # 线路不登记方向：历史班次（T01~T04）未标方向，按上行兼容；
    # T05/T06 显式登记下行，与上行共用同组站点，形成异向相邻到站。
    line = Line(code="B12", name="城东环线", planned_headway_min=8.0, bunch_threshold=3.0, large_threshold=15.0)
    db.add(line); db.flush()
    for trip_no, vehicle, offset, direction in SEED_SPECS:
        _create_trip(db, line, base, trip_no, vehicle, offset, direction)
    db.commit()

def upgrade_seed_data(db: Session) -> None:
    """旧库在分向功能上线前已种入 B12（仅 T01~T04 上行），幂等补上下行班次。

    这样既有开发库里也能复现：市民中心站 T05/T06 与上行到站时间相邻，
    旧逻辑会误报跨方向串车，分向判定后异向相邻不再出现在报告事件里。
    """
    line = db.scalar(select(Line).where(Line.code == "B12"))
    if line is None:
        return
    existing = set(db.scalars(select(Trip.trip_no).where(Trip.line_id == line.id)).all())
    added = False
    base = datetime(2026, 9, 17, 7, 0, 0)
    for trip_no, vehicle, offset, direction in SEED_SPECS:
        if trip_no in existing or direction is None:
            continue
        _create_trip(db, line, base, trip_no, vehicle, offset, direction)
        added = True
    if added:
        db.commit()
