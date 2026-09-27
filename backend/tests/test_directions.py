from app.services.directions import direction_label, normalize_direction, parse_direction, resolve_direction

def test_normalize_none_is_up():
    assert normalize_direction(None) == "up"
    assert normalize_direction("") == "up"
    assert normalize_direction("nonsense") == "up"

def test_normalize_aliases():
    assert normalize_direction("up") == "up"
    assert normalize_direction("UP") == "up"
    assert normalize_direction("上行") == "up"
    assert normalize_direction("down") == "down"
    assert normalize_direction("下行") == "down"

def test_parse_direction():
    assert parse_direction(None) is None
    assert parse_direction("") is None
    assert parse_direction("down") == "down"

def test_resolve_trip_over_line():
    assert resolve_direction("down", "up") == "down"

def test_resolve_falls_back_to_line_then_up():
    assert resolve_direction(None, "down") == "down"
    assert resolve_direction(None, None) == "up"

def test_direction_label():
    assert direction_label("down") == "下行"
    assert direction_label(None) == "上行"
