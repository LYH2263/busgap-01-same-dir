from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.models import Line, Trip
from app.services.directions import parse_direction, resolve_direction
router = APIRouter(prefix="/trips", tags=["trips"])

class DirectionIn(BaseModel):
    # "up" / "down" 登记班次方向；null 或空串清除，改回继承线路方向
    direction: str | None = None

def trip_dict(r: Trip) -> dict:
    resolved = resolve_direction(r.direction, r.line.direction)
    return {"id": r.id, "line_id": r.line_id, "trip_no": r.trip_no,
            "planned_depart": r.planned_depart.isoformat(), "vehicle_no": r.vehicle_no,
            "direction": r.direction, "line_direction": r.line.direction,
            "resolved_direction": resolved}

@router.get("")
def list_trips(line_id: int | None = None, direction: str | None = None, db: Session = Depends(get_db)):
    q = select(Trip).options(joinedload(Trip.line)).order_by(Trip.planned_depart)
    if line_id is not None: q = q.where(Trip.line_id == line_id)
    out = []
    for r in db.scalars(q).unique().all():
        if direction is not None and resolve_direction(r.direction, r.line.direction) != direction:
            continue
        out.append(trip_dict(r))
    return out

@router.patch("/{trip_id}")
def update_trip(trip_id: int, body: DirectionIn, db: Session = Depends(get_db)):
    trip = db.get(Trip, trip_id)
    if not trip: raise HTTPException(404, "班次不存在")
    trip.direction = parse_direction(body.direction)
    db.commit(); db.refresh(trip)
    line = db.get(Line, trip.line_id)
    return {"id": trip.id, "line_id": trip.line_id, "trip_no": trip.trip_no,
            "planned_depart": trip.planned_depart.isoformat(), "vehicle_no": trip.vehicle_no,
            "direction": trip.direction, "line_direction": line.direction if line else None,
            "resolved_direction": resolve_direction(trip.direction, line.direction if line else None)}
