import pytest

from django.contrib.auth import get_user_model
from django.core.cache import cache

from content_settings.models import ContentSetting, UserTagSetting

from tests.books.models import Book

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_admin(webtest_admin):
    cs = ContentSetting.objects.get(name="TITLE")
    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    resp.forms["contentsetting_form"]["value"] = "New Title"
    resp = resp.forms["contentsetting_form"].submit()
    assert resp.status_int == 302

    cs.refresh_from_db()
    assert cs.value == "New Title"

    resp = webtest_admin.get("/content-settings/fetch/title/")
    assert resp.status_int == 200
    assert resp.json == {"TITLE": "New Title"}


def test_admin_update_permission(webtest_admin):
    cs = ContentSetting.objects.get(name="BOOKS")
    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    resp.forms["contentsetting_form"][
        "value"
    ] = """
The Poplar,12,1
The Night of Taras,12,1
"""
    resp = resp.forms["contentsetting_form"].submit()
    assert resp.status_int == 302

    resp = webtest_admin.get("/content-settings/fetch/books/")
    assert resp.status_int == 200
    assert resp.json == {
        "BOOKS": [
            {"name": "The Poplar", "price": "12", "is_available": True},
            {"name": "The Night of Taras", "price": "12", "is_available": True},
        ]
    }


def test_admin_update_permission_forbidden(webtest_stuff):
    cs = ContentSetting.objects.get(name="BOOKS")
    init_value = cs.value
    resp = webtest_stuff.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    resp.forms["contentsetting_form"][
        "value"
    ] = """
The Poplar,12,1
The Night of Taras,12,1
"""
    resp = resp.forms["contentsetting_form"].submit()
    assert resp.status_int == 302

    resp = webtest_stuff.get("/admin/content_settings/contentsetting/")
    assert list(resp.context["messages"])[0].message.startswith(
        "You are not allowed to change"
    )
    assert resp.status_int == 200

    cs.refresh_from_db()
    assert cs.value == init_value


def test_admin_change_from_different_version(webtest_admin):
    cs = ContentSetting.objects.get(name="TITLE")
    cs.version = "NEW"
    cs.save(update_fields=["version"])
    initial_value = cs.value

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    resp.forms["contentsetting_form"]["value"] = "New Title"
    resp = resp.forms["contentsetting_form"].submit()
    assert resp.status_int == 302

    cs.refresh_from_db()
    assert cs.value == "New Title"

    resp = webtest_admin.get("/content-settings/fetch/title/")
    assert resp.status_int == 200
    assert resp.json == {"TITLE": initial_value}


def test_admin_change_but_cache_was_expired(webtest_admin):
    cs = ContentSetting.objects.get(name="TITLE")
    initial_value = cs.value

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    resp.forms["contentsetting_form"]["value"] = "New Title"
    resp = resp.forms["contentsetting_form"].submit()
    assert resp.status_int == 302

    cs.refresh_from_db()
    assert cs.value == "New Title"

    cache.clear()

    resp = webtest_admin.get("/content-settings/fetch/title/")
    assert resp.status_int == 200
    assert resp.json == {"TITLE": initial_value}


def test_context_processor(webtest_admin, webtest_user):
    resp = webtest_user.get("/books/")
    assert resp.status_int == 200
    assert resp.html.find("title").text == "Book Store"

    cs = ContentSetting.objects.get(name="TITLE")

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    resp.forms["contentsetting_form"]["value"] = "New Title"
    resp = resp.forms["contentsetting_form"].submit()
    assert resp.status_int == 302

    resp = webtest_user.get("/books/")
    assert resp.html.find("title").text == "New Title"


def test_preview_simple(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "TITLE",
            "value": "New Title",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {"html": "<pre>New Title</pre>"}


def test_preivew_format(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "OPEN_DATE",
            "value": "2023-01-01",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {"html": "<pre>datetime.date(2023, 1, 1)</pre>"}


def test_preivew_template_no_args(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "DESCRIPTION",
            "value": "{{CONTENT_SETTINGS.TITLE}} is the second best book store in the world",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {
        "html": "<pre>Book Store is the second best book store in the world</pre>"
    }


def test_no_preivew_template(webtest_admin):
    Book.objects.all().delete()

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "BOOK_RICH_DESCRIPTION",
            "value": "<b>{{book.title}}</b><br><i>{{book.description}}</i>",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {
        "html": "No preview (add at least one validator to preview_validators)"
    }


def test_preivew_template(webtest_admin):
    Book.objects.create(title="Kateryna", description="lorem ipsum")
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "BOOK_RICH_DESCRIPTION",
            "value": "<b>{{book.title}}</b><br><i>{{book.description}}</i>",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {"html": "<b>Kateryna</b><br><i>lorem ipsum</i>"}


def test_preview_validation_error(webtest_admin):
    cs = ContentSetting.objects.get(name="BOOKS_ON_HOME_PAGE")
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": cs.name,
            "value": "a lot",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {"error": "['Enter a whole number.']"}


def test_add_tag(webtest_admin):
    cs = ContentSetting.objects.get(name="TITLE")
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/add-tag/",
        {
            "name": cs.name,
            "tag": "important",
        },
    )

    assert resp.status_int == 200

    new_tag = UserTagSetting.objects.all().last()
    assert new_tag.name == cs.name
    assert new_tag.tag == "important"
    assert new_tag.user.username == "testadmin"

    resp = webtest_admin.get("/admin/content_settings/contentsetting/context-tags/")
    assert resp.status_int == 200
    assert '<a href="?tags=important">important</a><sup>1</sup>' in resp.content.decode(
        "utf-8"
    )

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert len(resp.html.find("table", {"id": "result_list"}).findAll("tr")) > 2

    resp = webtest_admin.get("/admin/content_settings/contentsetting/?tags=important")
    assert resp.status_int == 200
    assert len(resp.html.find("table", {"id": "result_list"}).findAll("tr")) == 2


def test_remove_tag(webtest_admin):
    initial_total_tags = UserTagSetting.objects.all().count()

    UserTagSetting.objects.create(
        name="TITLE",
        tag="important",
        user=get_user_model().objects.get(username="testadmin"),
    )

    assert initial_total_tags + 1 == UserTagSetting.objects.all().count()

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/remove-tag/",
        {
            "name": "TITLE-NEW",
            "tag": "important",
        },
    )

    assert resp.status_int == 200, resp.content.decode("utf-8")
    assert resp.json == {"error": "UserTagSetting matching query does not exist."}

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/remove-tag/",
        {
            "name": "TITLE",
            "tag": "important-NEW",
        },
    )

    assert resp.status_int == 200, resp.content.decode("utf-8")
    assert resp.json == {"error": "UserTagSetting matching query does not exist."}

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/remove-tag/",
        {
            "name": "TITLE",
            "tag": "important",
        },
    )

    assert resp.status_int == 200, resp.content.decode("utf-8")
    assert resp.json == {"success": True}

    assert initial_total_tags == UserTagSetting.objects.all().count()
