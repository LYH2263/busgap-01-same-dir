from datetime import datetime, timedelta
from app.services.bunch_engine import classify_gap, detect_bunching

def test_classify_bunching():
    assert classify_gap(2.0, 8.0, 3.0, 15.0)[0] == "bunching"

def test_classify_large():
    assert classify_gap(16.0, 8.0, 3.0, 15.0)[0] == "large_gap"

def test_classify_normal():
    assert classify_gap(8.0, 8.0, 3.0, 15.0)[0] == "normal"

def test_detect_bunching_events():
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "T1", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "T2", "actual_arrive": base + timedelta(minutes=2)},
        {"stop_name": "A", "trip_no": "T3", "actual_arrive": base + timedelta(minutes=20)},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert len(events) == 2
    assert events[0].status == "bunching"
    assert events[1].status == "large_gap"
    # 未标方向的历史到站统一按上行兼容
    assert all(e.direction == "up" for e in events)

def test_opposite_direction_adjacent_not_pair():
    # 时间顺序 上行 -> 下行(仅1分钟后) -> 上行：异向相邻不得判成串车/大间隔
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "U1", "actual_arrive": base, "direction": "up"},
        {"stop_name": "A", "trip_no": "D1", "actual_arrive": base + timedelta(minutes=1), "direction": "down"},
        {"stop_name": "A", "trip_no": "U2", "actual_arrive": base + timedelta(minutes=2), "direction": "up"},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert len(events) == 1
    assert events[0].earlier_trip == "U1"
    assert events[0].later_trip == "U2"
    assert events[0].direction == "up"
    assert events[0].status == "bunching"

def test_missing_direction_defaults_up():
    # 无方向历史班次与显式上行同桶，与下行不配对
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "H1", "actual_arrive": base},
        {"stop_name": "A", "trip_no": "U1", "actual_arrive": base + timedelta(minutes=2), "direction": "up"},
        {"stop_name": "A", "trip_no": "D1", "actual_arrive": base + timedelta(minutes=3), "direction": "down"},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert len(events) == 1
    assert (events[0].earlier_trip, events[0].later_trip, events[0].direction) == ("H1", "U1", "up")

def test_down_direction_uses_same_thresholds():
    # 阈值字段含义不变：下行同向大间隔照样判定
    base = datetime(2026, 1, 1, 8, 0)
    arrivals = [
        {"stop_name": "A", "trip_no": "D1", "actual_arrive": base, "direction": "down"},
        {"stop_name": "A", "trip_no": "D2", "actual_arrive": base + timedelta(minutes=16), "direction": "down"},
    ]
    events = detect_bunching(arrivals, 8.0, 3.0, 15.0)
    assert len(events) == 1
    assert events[0].status == "large_gap"
    assert events[0].direction == "down"
