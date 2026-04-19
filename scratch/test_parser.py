
from app.utils.time_parser import parse_datetime_flexible

test_cases = [
    "14.04 12:00",
    "14 04 12 00",
    "14/04 12-00",
    "14.4 12:00",
    "14041200",
    "14 4 12",
    "31.12 23:59"
]

for tc in test_cases:
    try:
        dt = parse_datetime_flexible(tc)
        print(f"Input: '{tc}' -> Result: {dt}")
    except Exception as e:
        print(f"Input: '{tc}' -> Error: {e}")
