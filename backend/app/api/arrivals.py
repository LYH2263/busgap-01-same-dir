from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.models import Arrival, Trip
from app.services.directions import normalize_direction, resolve_direction
router = APIRouter(prefix="/arrivals", tags=["arrivals"])

@router.get("")
def list_arrivals(line_id: int | None = None, direction: str | None = None, db: Session = Depends(get_db)):
    want = normalize_direction(direction) if direction is not None else None
    rows = db.scalars(select(Arrival).options(joinedload(Arrival.trip).joinedload(Trip.line)).order_by(Arrival.actual_arrive)).unique().all()
    out = []
    for r in rows:
        if line_id is not None and r.trip.line_id != line_id: continue
        resolved = resolve_direction(r.trip.direction, r.trip.line.direction)
        if want is not None and resolved != want: continue
        out.append({"id": r.id, "trip_id": r.trip_id, "trip_no": r.trip.trip_no, "line_id": r.trip.line_id,
                    "stop_name": r.stop_name, "stop_seq": r.stop_seq, "actual_arrive": r.actual_arrive.isoformat(),
                    "direction": resolved})
    return out
