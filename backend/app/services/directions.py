"""方向（上行/下行）登记与归一化。

历史线路、班次可能没有方向记录，统一按上行兼容（``normalize_direction``）。
检测与过滤时，登记了方向的班次以自身方向为准，未登记的继承线路方向。
"""
from __future__ import annotations

UP = "up"
DOWN = "down"

DIRECTION_LABELS = {UP: "上行", DOWN: "下行"}

# 常见写法 -> 标准值，方便接口/种子直接传中文或英文
_ALIASES = {
    "up": UP,
    "upward": UP,
    "上行": UP,
    "上": UP,
    "down": DOWN,
    "downward": DOWN,
    "下行": DOWN,
    "下": DOWN,
}


def normalize_direction(value: str | None) -> str:
    """归一化方向；未标方向（空值/无法识别）按上行兼容。"""
    if value is None:
        return UP
    key = str(value).strip().lower()
    return _ALIASES.get(key, UP)


def parse_direction(value: str | None) -> str | None:
    """解析用户提交的方向；空值返回 None（表示清除/继承），无法识别按上行兼容。"""
    if value is None:
        return None
    key = str(value).strip()
    if key == "":
        return None
    return normalize_direction(key)


def resolve_direction(trip_direction: str | None, line_direction: str | None = None) -> str:
    """班次未标方向时继承线路方向；两者都缺省按上行兼容。"""
    if trip_direction:
        return normalize_direction(trip_direction)
    if line_direction:
        return normalize_direction(line_direction)
    return UP


def direction_label(value: str | None) -> str:
    return DIRECTION_LABELS.get(normalize_direction(value), "上行")
