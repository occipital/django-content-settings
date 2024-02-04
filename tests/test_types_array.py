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

    assert var.give_python(
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
    ) == [
        "When I die, then bury me",
        "In my beloved Ukraine,",
        "My tomb upon a grave mound high",
        "Amid the spreading plain,",
        "So that the fields, the boundless steppes,",
        "The Dnieper's plunging shore",
        "My eyes could see, my ears could hear",
        "The mighty river roar.",
    ]


def test_simple_list_comment():
    var = SimpleStringsList()

    assert var.give_python(
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
    ) == [
        "When I die, then bury me",
        "So that the fields, the boundless steppes,",
        "The Dnieper's plunging shore",
        "My eyes could see, my ears could hear",
        "The mighty river roar.",
    ]


def test_simple_list_window_new_line():
    var = SimpleStringsList()

    assert var.give_python("windows\r\nlinebreaks") == ["windows", "linebreaks"]


def test_simple_list_comment_starts_with():
    var = SimpleStringsList(comment_starts_with="//")

    assert var.give_python(
        """
        When I die, then bury me
        In my beloved Ukraine,
//        My tomb upon a grave mound high
        Amid the spreading plain,
        So that the fields, the boundless steppes,
        The Dnieper's plunging shore
        My eyes could see, my ears could hear
        The mighty river roar.
                         """
    ) == [
        "When I die, then bury me",
        "In my beloved Ukraine,",
        "Amid the spreading plain,",
        "So that the fields, the boundless steppes,",
        "The Dnieper's plunging shore",
        "My eyes could see, my ears could hear",
        "The mighty river roar.",
    ]


class SimpleIntsList(TypedStringsList):
    line_type = SimpleInt()


def test_typed_list():
    var = SimpleIntsList()

    assert (
        var.give_python(
            """
        1
        2
        3
                         
        """
        )
        == [1, 2, 3]
    )


def test_typed_list_with_comment():
    var = SimpleIntsList()

    assert (
        var.give_python(
            """
        1
        #2
        3
                         
        """
        )
        == [1, 3]
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
    assert error.value.message == "item #4: Enter a whole number."
