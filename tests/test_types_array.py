import pytest

from django.core.exceptions import ValidationError

from content_settings.types.basic import SimpleInt
from content_settings.types.array import (
    SimpleStringsList,
    TypedStringsList,
)

pytestmark = [pytest.mark.django_db]


def test_simple_list():
    var = SimpleStringsList()

    assert (
        var.to_python(
            """
        When I die, then bury me
        In my beloved Ukraine,
        My tomb upon a grave mound high
        Amid the spreading plain,
        So that the fields, the boundless steppes,
        The Dnieper's plunging shore
        My eyes could see, my ears could hear
        The mighty river roar.
                         """
        )
        == [
            "When I die, then bury me",
            "In my beloved Ukraine,",
            "My tomb upon a grave mound high",
            "Amid the spreading plain,",
            "So that the fields, the boundless steppes,",
            "The Dnieper's plunging shore",
            "My eyes could see, my ears could hear",
            "The mighty river roar.",
        ]
    )

    assert (
        var.to_python(
            """
        When I die, then bury me
        # In my beloved Ukraine,
        # My tomb upon a grave mound high
        # Amid the spreading plain,
        So that the fields, the boundless steppes,
        The Dnieper's plunging shore
        My eyes could see, my ears could hear
        The mighty river roar.
                         """
        )
        == [
            "When I die, then bury me",
            "So that the fields, the boundless steppes,",
            "The Dnieper's plunging shore",
            "My eyes could see, my ears could hear",
            "The mighty river roar.",
        ]
    )

    assert var.to_python("windows\r\nlinebreaks") == ["windows", "linebreaks"]


class SimpleIntsList(TypedStringsList):
    line_type = SimpleInt()


def test_typed_list():
    var = SimpleIntsList()

    assert (
        var.to_python(
            """
        1
        2
        3
                         
        """
        )
        == [1, 2, 3]
    )


def test_typed_list_validate():
    var = SimpleIntsList()

    with pytest.raises(ValidationError) as error:
        var.validate_value(
            """
            1
            2
            3
            a
        """
        )
    assert error.value.message == "Line 5: Enter a whole number."
