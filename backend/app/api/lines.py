from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Line
from app.services.directions import parse_direction
router = APIRouter(prefix="/lines", tags=["lines"])

class DirectionIn(BaseModel):
    # "up" / "down" 登记方向；null 或空串清除登记（班次未标时按上行兼容）
    direction: str | None = None

def line_dict(r: Line) -> dict:
    return {"id": r.id, "code": r.code, "name": r.name, "planned_headway_min": r.planned_headway_min,
            "bunch_threshold": r.bunch_threshold, "large_threshold": r.large_threshold,
            "direction": r.direction}

@router.get("")
def list_lines(db: Session = Depends(get_db)):
    rows = db.scalars(select(Line).order_by(Line.id)).all()
    return [line_dict(r) for r in rows]

@router.patch("/{line_id}")
def update_line(line_id: int, body: DirectionIn, db: Session = Depends(get_db)):
    line = db.get(Line, line_id)
    if not line: raise HTTPException(404, "线路不存在")
    line.direction = parse_direction(body.direction)
    db.commit(); db.refresh(line)
    return line_dict(line)
