import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.models import Arrival, BunchReport, Line, Trip
from app.services.bunch_engine import detect_bunching, events_to_dicts
from app.services.directions import normalize_direction, resolve_direction
router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("")
def list_reports(db: Session = Depends(get_db)):
    rows = db.scalars(select(BunchReport).order_by(BunchReport.id.desc())).all()
    return [{"id": r.id, "line_id": r.line_id, "stop_name": r.stop_name,
             "created_at": r.created_at.isoformat(), "events": json.loads(r.summary_json)} for r in rows]

def _load_arrival_payload(db: Session, line_id: int, stop_name: str | None, direction: str | None) -> list[dict]:
    want = normalize_direction(direction) if direction is not None else None
    q = (select(Arrival)
         .join(Trip, Arrival.trip_id == Trip.id)
         .options(joinedload(Arrival.trip).joinedload(Trip.line))
         .where(Trip.line_id == line_id))
    if stop_name is not None:
        q = q.where(Arrival.stop_name == stop_name)
    payload = []
    for a in db.scalars(q).unique().all():
        resolved = resolve_direction(a.trip.direction, a.trip.line.direction)
        if want is not None and resolved != want: continue
        payload.append({"stop_name": a.stop_name, "trip_no": a.trip.trip_no,
                        "actual_arrive": a.actual_arrive, "direction": resolved})
    return payload

@router.post("/run")
def run_detection(line_id: int, stop_name: str | None = None, direction: str | None = None, db: Session = Depends(get_db)):
    line = db.get(Line, line_id)
    if not line: raise HTTPException(404, "线路不存在")
    # 不传方向时仍按方向分桶判定，异向相邻不会产生事件
    payload = _load_arrival_payload(db, line_id, stop_name, direction)
    events = detect_bunching(payload, line.planned_headway_min, line.bunch_threshold, line.large_threshold)
    data = events_to_dicts(events)
    report = BunchReport(line_id=line_id, stop_name=stop_name or "*", created_at=datetime.utcnow(),
                         summary_json=json.dumps(data, ensure_ascii=False))
    db.add(report); db.commit(); db.refresh(report)
    return {"id": report.id, "events": data}

@router.get("/suggestions")
def suggestions(line_id: int, direction: str | None = None, db: Session = Depends(get_db)):
    result = run_detection(line_id=line_id, stop_name=None, direction=direction, db=db)
    return {"line_id": line_id, "suggestions": [e for e in result["events"] if e["status"] != "normal"]}

@router.get("/timeline")
def timeline(line_id: int, stop_name: str = "市民中心", direction: str | None = None, db: Session = Depends(get_db)):
    want = normalize_direction(direction) if direction is not None else None
    line = db.get(Line, line_id)
    if not line: raise HTTPException(404, "线路不存在")
    trips = db.scalars(select(Trip).where(Trip.line_id == line_id)).all()
    trip_ids = [t.id for t in trips]
    trip_dir_map = {t.id: resolve_direction(t.direction, line.direction) for t in trips}
    trip_no_map = {t.id: t.trip_no for t in trips}
    arrivals = sorted(db.scalars(select(Arrival).where(Arrival.trip_id.in_(trip_ids), Arrival.stop_name == stop_name)).all(),
                      key=lambda a: a.actual_arrive)
    marks = []
    for a in arrivals:
        resolved = trip_dir_map.get(a.trip_id)
        if want is not None and resolved != want: continue
        marks.append((a, resolved))
    if not marks: return {"stop_name": stop_name, "marks": []}
    t0 = marks[0][0].actual_arrive
    span = max((marks[-1][0].actual_arrive - t0).total_seconds(), 1)
    out = [{"trip_no": trip_no_map[a.trip_id], "actual_arrive": a.actual_arrive.isoformat(),
            "direction": resolved,
            "pct": round((a.actual_arrive - t0).total_seconds() / span * 100, 2)} for a, resolved in marks]
    return {"stop_name": stop_name, "marks": out}
