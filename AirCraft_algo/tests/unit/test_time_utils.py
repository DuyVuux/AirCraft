from src.model.time import parse_time, timestamp_to_iso, format_duration


class TestParseTime:
    def test_iso_format_utc(self):
        result = parse_time("2024-12-05T08:00:00Z")
        assert result > 0

    def test_iso_format_offset(self):
        result = parse_time("2024-12-05T08:00:00+00:00")
        assert result > 0

    def test_roundtrip(self):
        iso_str = "2024-12-05T08:00:00Z"
        ts = parse_time(iso_str)
        back = timestamp_to_iso(ts)
        assert parse_time(back) == ts

    def test_order_preserved(self):
        t1 = parse_time("2024-12-05T08:00:00Z")
        t2 = parse_time("2024-12-05T09:00:00Z")
        assert t2 > t1
        assert t2 - t1 == 3600


class TestFormatDuration:
    def test_seconds(self):
        assert format_duration(45) == "45s"

    def test_minutes(self):
        assert format_duration(120) == "2m"

    def test_mixed(self):
        assert format_duration(90) == "1m30s"

    def test_hours(self):
        assert format_duration(3661) == "1h1m"

    def test_zero(self):
        assert format_duration(0) == "0s"
