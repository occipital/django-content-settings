import pytest
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import Client

from content_settings.models import ContentSetting
from content_settings.types.basic import (
    SimpleText,
    SimpleDecimal,
    SimpleHTML,
    SimpleTextPreview,
)
from content_settings.types.mixins import mix, DictSuffixesMixin
from content_settings.types.array import (
    SplitByFirstLine,
    split_validator_in,
    NOT_FOUND,
    SPLIT_FAIL,
)
from content_settings.types.each import EACH_SUFFIX
from content_settings.types.template import DjangoModelTemplateHTML
from content_settings.types import optional

from tests.books.models import Book

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_empty_line():
    var = SplitByFirstLine(split_default_key="EN")
    var.validate_value("")
    assert var.to_python("") == {"EN": ""}
    assert var.give_python("") == ""


def test_without_splitter():
    var = SplitByFirstLine(split_default_key="EN")
    var.validate_value("A Simple Line")
    assert var.to_python("A Simple Line") == {"EN": "A Simple Line"}
    assert var.give_python("A Simple Line") == "A Simple Line"


def test_with_only_one_value():
    var = SplitByFirstLine(split_default_key="EN")
    text = """
==== EN ====
A Simple Line
    """.strip()
    var.validate_value(text)
    assert var.to_python(text) == {"EN": "A Simple Line"}
    assert var.give_python(text) == "A Simple Line"


def test_with_two_values():
    var = SplitByFirstLine(split_default_key="EN")
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    var.validate_value(text)
    assert var.to_python(text) == {"EN": "A Simple Line", "UA": "Проста Лінія"}
    assert var.give_python(text) == "A Simple Line"
    assert var.give_python(text, "ua") == "Проста Лінія"


def test_with_two_values_one_valid():
    var = SplitByFirstLine(
        split_default_key="EN", split_key_validator=split_validator_in(["EN", "UA"])
    )
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
==== FR ====
Une ligne simple
    """.strip()
    var.validate_value(text)
    assert var.to_python(text) == {
        "EN": "A Simple Line",
        "UA": "Проста Лінія\n==== FR ====\nUne ligne simple",
    }


def test_with_two_values_one_valid_2():
    var = SplitByFirstLine(
        split_default_key="EN", split_key_validator=split_validator_in(["EN", "UA"])
    )
    text = """
==== EN ====
A Simple Line
==== FR ====
Une ligne simple
==== UA ====
Проста Лінія
    """.strip()
    var.validate_value(text)
    assert var.to_python(text) == {
        "EN": "A Simple Line\n==== FR ====\nUne ligne simple",
        "UA": "Проста Лінія",
    }


def test_with_two_values_one_valid_raise():
    var = SplitByFirstLine(
        split_default_key="EN",
        split_key_validator=split_validator_in(["EN", "UA"]),
        split_key_validator_failed=SPLIT_FAIL.RAISE,
    )
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
==== FR ====
Une ligne simple
    """.strip()
    with pytest.raises(ValidationError) as err:
        var.validate_value(text)

    assert err.value.message == "Invalid split key: FR in line 5"


def test_with_two_decimal_values():
    var = SplitByFirstLine(split_default_key="EN", split_type=SimpleDecimal())
    text = """
==== EN ====
4.5
==== UA ====
3.3
    """.strip()
    var.validate_value(text)
    assert var.to_python(text) == {"EN": Decimal("4.5"), "UA": Decimal("3.3")}


def test_validate_value():
    var = SplitByFirstLine(split_default_key="EN", split_type=SimpleDecimal())
    text = """
==== EN ====
4.5
==== UA ====
second
    """.strip()
    with pytest.raises(ValidationError) as err:
        var.validate_value(text)
    assert err.value.message == "key UA: Enter a number."

    text = """
==== EN ====
one
==== UA ====
second
    """.strip()
    with pytest.raises(ValidationError) as err:
        var.validate_value(text)
    assert err.value.message == "key EN: Enter a number."


def test_default_chooser_two_possible():
    choice = "EN"

    def split_default_chooser(value):
        return choice

    var = SplitByFirstLine(
        split_default_key="EN", split_default_chooser=split_default_chooser
    )
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    var.validate_value(text)
    assert var.give_python(text) == "A Simple Line"

    choice = "UA"
    assert var.give_python(text) == "Проста Лінія"


def test_default_chooser_one_possible():
    choice = "EN"

    def split_default_chooser(value):
        return choice

    var = SplitByFirstLine(
        split_default_key="EN", split_default_chooser=split_default_chooser
    )
    text = """
A Simple Line
    """.strip()
    var.validate_value(text)
    assert var.give_python(text) == "A Simple Line"


def test_split_NOT_FOUND_DEFAULT():
    var = SplitByFirstLine(split_default_key="EN", split_not_found=NOT_FOUND.DEFAULT)
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text, "ff") == "A Simple Line"


def test_split_NOT_FOUND_VALUE():
    var = SplitByFirstLine(
        split_default_key="EN",
        split_not_found=NOT_FOUND.VALUE,
        split_not_found_value="Not Found",
    )
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text, "ff") == "Not Found"


def test_split_NOT_FOUND_KEY_ERROR():
    var = SplitByFirstLine(split_default_key="EN", split_not_found=NOT_FOUND.KEY_ERROR)
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()

    with pytest.raises(KeyError) as err:
        var.give_python(text, "ff")


def test_split_key_validator():
    def split_validator(value):
        if value not in ["EN", "UA"]:
            raise ValidationError(f"Wrong Name {value}")

    var = SplitByFirstLine(split_default_key="EN", split_key_validator=split_validator)
    text = """
==== EN ====
4.5
==== UA ====
70
    """.strip()
    var.validate_value(text)

    text = """
==== EN ====
4.5
==== UA ====
70
==== FF ====
80
    """.strip()

    with pytest.raises(ValidationError) as err:
        var.validate_value(text)
    assert err.value.message == "Wrong Name FF"


class TruncText(DictSuffixesMixin, SimpleText):
    suffixes = {
        "trunc": lambda text, max_length=10: (text[: max_length - 3] + "...")
        if len(text) > max_length
        else text
    }


class SplitTruncText(SplitByFirstLine):
    split_type = TruncText()
    split_default_key = "EN"
    is_ua = False

    def split_default_choose(self, value):
        return "UA" if self.is_ua else "EN"


def test_split_trunc_text():
    var = SplitTruncText()
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text) == "A Simple Line"
    assert var.give_python(text, "ua") == "Проста Лінія"

    var.is_ua = True
    assert var.give_python(text) == "Проста Лінія"
    assert var.give_python(text, "en") == "A Simple Line"


def test_split_trunc_text_use_parent():
    var = SplitTruncText(each_suffix_use=EACH_SUFFIX.USE_PARENT)
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text) == "A Simple Line"
    assert var.give_python(text, "trunc") == "A Simpl..."


def test_split_trunc_text_split_own():
    var = SplitTruncText(
        each_suffix_use=EACH_SUFFIX.SPLIT_OWN, each_suffix_splitter="_to_"
    )
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text) == "A Simple Line"
    assert var.give_python(text, "ua") == "Проста Лінія"
    assert var.give_python(text, "trunc") == "A Simple Line"
    assert var.give_python(text, "ua_to_trunc") == "Проста ..."
    assert var.give_python(text, "en_to_trunc") == "A Simpl..."


def test_split_trunc_text_split_parent():
    var = SplitTruncText(
        each_suffix_use=EACH_SUFFIX.SPLIT_PARENT, each_suffix_splitter="_to_"
    )
    text = """
==== EN ====
A Simple Line
==== UA ====
Проста Лінія
    """.strip()
    assert var.give_python(text) == "A Simple Line"
    with pytest.raises(KeyError) as err:
        var.give_python(text, "ua")

    assert var.give_python(text, "trunc") == "A Simpl..."

    var.is_ua = True
    assert var.give_python(text, "trunc") == "Проста ..."
    assert var.give_python(text, "en_to_trunc") == "A Simpl..."


def test_split_translation_with_default_value():
    client = Client()
    resp = client.get("/content-settings/fetch/COMPANY_DESCRIPTION/")
    assert resp.status_code == 200
    assert resp.json() == {
        "COMPANY_DESCRIPTION": "The best Company",
    }

    resp = client.get(
        "/content-settings/fetch/COMPANY_DESCRIPTION/", HTTP_ACCEPT_LANGUAGE="ua"
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "COMPANY_DESCRIPTION": "The best Company",
    }


def test_split_translation_with_available_translations():
    cs = ContentSetting.objects.get(name="COMPANY_DESCRIPTION")
    cs.value = """
!!!! EN !!!!
The best Company
!!!! ES !!!!
La mejor empresa
    """.strip()
    cs.save()

    client = Client()
    resp = client.get(
        "/content-settings/fetch/COMPANY_DESCRIPTION/",
        headers={"accept-language": "en"},
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "COMPANY_DESCRIPTION": "The best Company",
    }

    resp = client.get(
        "/content-settings/fetch/COMPANY_DESCRIPTION/",
        headers={"accept-language": "es"},
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "COMPANY_DESCRIPTION": "La mejor empresa",
    }


def test_admin_preview_default(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "COMPANY_DESCRIPTION",
            "value": "This is not so long, but very interesting text",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {
        "html": "<pre>This is not so long, but very interesting text</pre>",
    }


def test_admin_preview_with_header(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "COMPANY_DESCRIPTION",
            "value": """
==== EN ====
This is not so long, but very interesting text
""".strip(),
        },
    )

    assert resp.status_int == 200
    assert resp.json == {
        "html": "<pre>This is not so long, but very interesting text</pre>",
    }


def test_admin_preview_with_two_langs(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "COMPANY_DESCRIPTION",
            "value": """
==== EN ====
This is not so long, but very interesting text
==== UA ====
Це не так довго, але дуже цікавий текст
""".strip(),
        },
    )

    assert resp.status_int == 200
    assert resp.json == {
        "html": '<div> <b>EN</b>  <a class="cs_set_params" data-param-suffix="UA">UA</a> </div><pre>This is not so long, but very interesting text</pre>',
    }


def test_admin_preview_with_two_langs_ua(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "COMPANY_DESCRIPTION",
            "p_suffix": "UA",
            "value": """
==== EN ====
This is not so long, but very interesting text
==== UA ====
Це не так довго, але дуже цікавий текст
""".strip(),
        },
    )

    assert resp.status_int == 200
    assert resp.json == {
        "html": '<div> <a class="cs_set_params">EN</a>  <b>UA</b> </div><pre>Це не так довго, але дуже цікавий текст</pre>',
    }


class SplitEmail(SplitByFirstLine):
    split_type = {
        "BODY": SimpleHTML(optional),
        "SUBJECT": SimpleTextPreview(),
    }
    split_default_key = "BODY"


def test_split_email_only_body():
    var = SplitEmail()
    text = """
This is Body
"""
    assert var.give_python(text) == "This is Body"
    assert var.give_python(text, "subject") == ""


def test_split_email_only_body_with_splitter():
    var = SplitEmail()
    text = """=== BODY ===
This is Body
"""
    assert var.give_python(text) == "This is Body"
    assert var.give_python(text, "subject") == ""


def test_split_email_with_subject():
    var = SplitEmail()
    text = """=== BODY ===
This is Body
=== SUBJECT ===
This is Subject
"""
    assert var.give_python(text) == "This is Body"
    assert var.give_python(text, "subject") == "This is Subject"


def test_split_email_preview_with_subject():
    var = SplitEmail()
    text = """=== BODY ===
This is Body
=== SUBJECT ===
This is Subject
"""
    assert (
        var.get_admin_preview_value(text, "VAR")
        == '<div> <b>BODY</b>  <a class="cs_set_params" data-param-suffix="SUBJECT">SUBJECT</a> </div>This is Body'
    )


def test_split_email_preview_with_subject_check_subject():
    var = SplitEmail()
    text = """=== BODY ===
This is Body
=== SUBJECT ===
This is Subject
"""
    assert (
        var.get_admin_preview_value(text, "VAR", suffix="SUBJECT")
        == '<div> <a class="cs_set_params">BODY</a>  <b>SUBJECT</b> </div><pre>This is Subject</pre>'
    )


def test_split_with_django_template():
    Book.objects.create(title="The Beatles", description="The best band")

    var = SplitByFirstLine(
        "",
        split_type={
            "SUBJECT": SimpleTextPreview(),
            "BODY": DjangoModelTemplateHTML(
                "",
                model_queryset=Book.objects.all(),
                obj_name="book",
            ),
        },
        split_key_validator=split_validator_in(["BODY", "SUBJECT"]),
        split_default_key="BODY",
    )
    text = """Hi {{book.title}}, this is Body"""
    assert (
        var.get_admin_preview_value(text, "VAR")
        == '<div> <b>BODY</b>  <a class="cs_set_params" data-param-suffix="SUBJECT">SUBJECT</a> </div>Hi The Beatles, this is Body'
    )


def test_split_with_django_template_full():
    Book.objects.create(title="The Beatles", description="The best band")

    var = SplitByFirstLine(
        "",
        split_type={
            "SUBJECT": SimpleTextPreview(),
            "BODY": DjangoModelTemplateHTML(
                "",
                model_queryset=Book.objects.all(),
                obj_name="book",
            ),
        },
        split_key_validator=split_validator_in(["BODY", "SUBJECT"]),
        split_default_key="BODY",
    )
    text = """=== BODY ===
Hi {{book.title}}, this is Body
=== SUBJECT ===
This is Subject
"""
    assert (
        var.get_admin_preview_value(text, "VAR")
        == '<div> <b>BODY</b>  <a class="cs_set_params" data-param-suffix="SUBJECT">SUBJECT</a> </div>Hi The Beatles, this is Body'
    )


def test_split_with_django_template_subject():
    Book.objects.create(title="The Beatles", description="The best band")

    var = SplitByFirstLine(
        "",
        split_type={
            "SUBJECT": SimpleTextPreview(""),
            "BODY": DjangoModelTemplateHTML(
                "",
                model_queryset=Book.objects.all(),
                obj_name="book",
            ),
        },
        split_key_validator=split_validator_in(["BODY", "SUBJECT"]),
        split_default_key="BODY",
    )
    text = """=== BODY ===
Hi {{book.title}}, this is Body
=== SUBJECT ===
This is Subject - {{book.title}}
"""
    assert (
        var.get_admin_preview_value(text, "VAR", suffix="SUBJECT")
        == '<div> <a class="cs_set_params">BODY</a>  <b>SUBJECT</b> </div><pre>This is Subject - {{book.title}}</pre>'
    )
