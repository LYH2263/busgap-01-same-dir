"""Bus bunching: planned headway vs actual arrival gaps.

串车/大间隔判定按「站点 + 方向」分别进行：同一站点只把相同方向的相邻
到站拿来算间隔，上行紧挨下行不会被判成一对串车或大间隔。未标方向的
到站记录按上行兼容（见 app.services.directions）。
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime

from app.services.directions import normalize_direction

@dataclass
class GapEvent:
    stop_name: str
    earlier_trip: str
    later_trip: str
    gap_min: float
    planned_headway_min: float
    status: str
    suggestion: str
    direction: str = "up"

def classify_gap(gap_min: float, planned_headway_min: float, bunch_threshold: float, large_threshold: float) -> tuple[str, str]:
    if gap_min < bunch_threshold:
        return ("bunching", f"间隔 {gap_min:.1f} 分钟低于串车阈值 {bunch_threshold}，建议后车缓行或抽稀。")
    if gap_min > large_threshold:
        return ("large_gap", f"间隔 {gap_min:.1f} 分钟超过大间隔阈值 {large_threshold}，建议前车减速或加发。")
    return ("normal", f"间隔接近计划 {planned_headway_min:.1f} 分钟，保持即可。")

def detect_bunching(arrivals: list[dict], planned_headway_min: float, bunch_threshold: float, large_threshold: float) -> list[GapEvent]:
    # 先按方向分桶，再按站点分桶；异向到站即使时间相邻也不参与间隔计算
    by_stop_dir: dict[tuple[str, str], list[dict]] = {}
    for a in arrivals:
        direction = normalize_direction(a.get("direction"))
        by_stop_dir.setdefault((a["stop_name"], direction), []).append(a)
    events: list[GapEvent] = []
    for (stop, direction), items in by_stop_dir.items():
        items = sorted(items, key=lambda x: x["actual_arrive"])
        for i in range(1, len(items)):
            prev, cur = items[i - 1], items[i]
            gap_min = (cur["actual_arrive"] - prev["actual_arrive"]).total_seconds() / 60.0
            status, suggestion = classify_gap(gap_min, planned_headway_min, bunch_threshold, large_threshold)
            events.append(GapEvent(stop, prev["trip_no"], cur["trip_no"], round(gap_min, 2),
                                   planned_headway_min, status, suggestion, direction))
    events.sort(key=lambda e: (e.stop_name, e.direction, e.gap_min))
    return events

def events_to_dicts(events: list[GapEvent]) -> list[dict]:
    return [asdict(e) for e in events]
