from datetime import datetime

from app.scripts.import_data import parse_created_date, parse_rubrics


def test_parse_rubrics():
    value = "['one', 'two']"

    assert parse_rubrics(value) == ["one", "two"]


def test_parse_empty_rubrics():
    assert parse_rubrics("") == []


def test_parse_created_date():
    result = parse_created_date("2019-09-01 09:48:41")

    assert result == datetime(2019, 9, 1, 9, 48, 41)
