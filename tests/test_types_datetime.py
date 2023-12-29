import pytest
from datetime import datetime, date, time, timedelta

from django.core.exceptions import ValidationError

from content_settings.types.datetime import (
    DateTimeString,
    DateString,
    TimeString,
    SimpleTimedelta,
)

pytestmark = [pytest.mark.django_db]


def test_datetime():
    var = DateTimeString()

    assert var.to_python("2020-01-01 00:00:00").replace(tzinfo=None) == datetime(
        2020, 1, 1
    )


def test_datetime_empty_is_none():
    var = DateTimeString()

    assert var.to_python("") is None
    assert var.to_python(" ") is None


def test_date():
    var = DateString()

    assert var.to_python("2020-01-01") == date(2020, 1, 1)
    assert var.to_python("") is None


def test_date_input_format():
    var = DateString("", input_formats="%d/%m/%Y")

    assert var.to_python("03/01/2020") == date(2020, 1, 3)

    with pytest.raises(ValidationError):
        var.to_python("2020-01-03")


def test_time():
    var = TimeString()

    assert var.to_python("00:00:00") == time(0, 0, 0)
    assert var.to_python("03:30") == time(3, 30)


def test_timedelta():
    var = SimpleTimedelta()

    assert var.to_python("1d") == timedelta(days=1)
    assert var.to_python("1d 2h") == timedelta(days=1, hours=2)
    assert var.to_python("") == timedelta()
