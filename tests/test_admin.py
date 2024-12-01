import pytest
import re

from django.contrib.auth import get_user_model
from django.core.cache import cache

from content_settings.models import ContentSetting, UserTagSetting
from content_settings.models import UserPreview, ContentSetting, UserPreviewHistory

from tests.books.models import Book

from .tools import extract_messages
from tests import testing_settings_full, testing_settings_min

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

    resp = webtest_admin.get("/books/fetch/all/")
    assert resp.status_int == 200
    assert resp.json["TITLE"] == "New Title"


@pytest.mark.skipif(
    not testing_settings_full, reason="skipping because not testing_settings_full"
)
def test_admin_checksum_check(webtest_admin):
    cs = ContentSetting.objects.get(name="TITLE")
    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    resp2 = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")

    resp.forms["contentsetting_form"]["value"] = "New Title"
    resp = resp.forms["contentsetting_form"].submit()
    assert resp.status_int == 302

    cs.refresh_from_db()
    assert cs.value == "New Title"

    resp2.forms["contentsetting_form"]["value"] = "Super Title"
    resp2 = resp2.forms["contentsetting_form"].submit()
    assert resp2.status_int == 302

    cs.refresh_from_db()
    assert cs.value == "New Title"


def test_admin_list_view(webtest_admin):
    cs = ContentSetting.objects.get(name="BOOKS_ON_HOME_PAGE")
    resp = webtest_admin.get(
        f"/admin/content_settings/contentsetting/?q=BOOKS_ON_HOME_PAGE"
    )
    assert resp.status_int == 200

    resp.forms["changelist-form"]["form-0-value"] = "4"
    resp = resp.forms["changelist-form"].submit(name="_save")

    cs.refresh_from_db()
    assert cs.value == "4"


@pytest.mark.skipif(
    not testing_settings_full, reason="skipping because of  not testing_settings_full"
)
def test_admin_list_view_checksum_check(webtest_admin):
    cs = ContentSetting.objects.get(name="BOOKS_ON_HOME_PAGE")
    resp = webtest_admin.get(
        f"/admin/content_settings/contentsetting/?q=BOOKS_ON_HOME_PAGE"
    )
    assert resp.status_int == 200

    resp2 = webtest_admin.get(
        f"/admin/content_settings/contentsetting/?q=BOOKS_ON_HOME_PAGE"
    )
    assert resp2.status_int == 200

    resp.forms["changelist-form"]["form-0-value"] = "4"
    resp = resp.forms["changelist-form"].submit(name="_save")

    resp2.forms["changelist-form"]["form-0-value"] = "5"
    resp2 = resp2.forms["changelist-form"].submit(name="_save")

    cs.refresh_from_db()
    assert cs.value == "4"


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

    resp = webtest_admin.get("/books/fetch/all/")
    assert resp.status_int == 200
    assert resp.json["BOOKS"] == [
        {"name": "The Poplar", "price": "12", "is_available": True},
        {"name": "The Night of Taras", "price": "12", "is_available": True},
    ]


def test_admin_change_from_different_version(webtest_admin):
    resp = webtest_admin.get("/books/fetch/all/")
    assert resp.status_int == 200
    assert resp.json["TITLE"] == "Book Store"
    initial_value = resp.json["TITLE"]

    ContentSetting.objects.filter(name="TITLE").update(version="NEW")
    cs = ContentSetting.objects.get(name="TITLE")

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    resp.forms["contentsetting_form"]["value"] = "New Title"
    resp = resp.forms["contentsetting_form"].submit()
    assert resp.status_int == 302

    cs.refresh_from_db()
    assert cs.value == "New Title"

    resp = webtest_admin.get("/books/fetch/all/")
    assert resp.status_int == 200
    assert resp.json["TITLE"] == initial_value


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

    resp = webtest_admin.get("/books/fetch/all/")
    assert resp.status_int == 200
    assert resp.json["TITLE"] == initial_value


def test_admin_update(webtest_admin, webtest_user):
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


def test_admin_update_history(webtest_admin):
    cs = ContentSetting.objects.get(name="TITLE")
    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/history/")
    assert resp.status_int == 200
    assert len(resp.html.find("table", {"id": "change-history"}).find_all("tr")) == 2

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    resp.forms["contentsetting_form"]["value"] = "New Title"
    resp = resp.forms["contentsetting_form"].submit()
    assert resp.status_int == 302

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/history/")
    assert resp.status_int == 200

    assert len(resp.html.find("table", {"id": "change-history"}).find_all("tr")) == 3
    assert (
        re.sub(
            r"\s+",
            " ",
            resp.html.find("table", {"id": "change-history"})
            .find_all("tr")[1]
            .find_all("td")[0]
            .text.replace("\n", " "),
        ).strip()
        == "Changed by user testadmin"
    )


def test_preview_simple(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "TITLE",
            "value": "New Title",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {"html": ""}


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
        "html": "No preview (add at least one call_validator in validators)"
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
            "tag": "favorites",
        },
    )

    assert resp.status_int == 200

    new_tag = UserTagSetting.objects.all().last()
    assert new_tag.name == cs.name
    assert new_tag.tag == "favorites"
    assert new_tag.user.username == "testadmin"

    resp = webtest_admin.get("/admin/content_settings/contentsetting/context-tags/")
    assert resp.status_int == 200
    assert '<a href="?tags=favorites">⭐</a><sup>1</sup>' in resp.content.decode(
        "utf-8"
    )

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert len(resp.html.find("table", {"id": "result_list"}).findAll("tr")) > 2

    resp = webtest_admin.get("/admin/content_settings/contentsetting/?tags=favorites")
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


def test_preview_non_existed_name(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "TITLE-NEW",
            "value": "New Title",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {"html": "", "error": "Invalid name"}


def test_preview_menu_default(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "INTERESTING_TEXT",
            "value": "This is not so long, but very interesting text",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {
        "html": '<div> <b>default</b>  <a class="cs_set_params" data-param-suffix="trim">trim</a> </div><pre>This is not so long, but very interesting text</pre>',
    }


def test_preview_menu_trim(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "INTERESTING_TEXT",
            "value": "This is not so long, but very interesting text",
            "p_suffix": "trim",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {
        "html": '<div> <a class="cs_set_params">default</a>  <b>trim</b> </div><pre>This is...</pre>',
    }


def test_view_permission_staff_for_awesome_staff(webtest_staff):
    resp = webtest_staff.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert "REFFERAL_URL" in resp.html.text
    assert "AWESOME_PASS" not in resp.html.text


def test_view_permission_staff_for_awesome_staff_abs_url(webtest_staff):
    cs = ContentSetting.objects.get(name="AWESOME_PASS")

    resp = webtest_staff.get(
        f"/admin/content_settings/contentsetting/{cs.id}/change/", expect_errors=True
    )
    assert resp.status_int == 403


def test_view_permission_superuser_for_awesome_staff(webtest_admin):
    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert "REFFERAL_URL" in resp.html.text
    assert "AWESOME_PASS" in resp.html.text


def test_view_permission_superuser_for_awesome_staff_abs_url(webtest_admin):
    cs = ContentSetting.objects.get(name="AWESOME_PASS")

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200


def test_view_history_permission_superuser(webtest_admin):
    cs = ContentSetting.objects.get(name="REFFERAL_URL")

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/history/")
    assert resp.status_int == 200


def test_view_history_permission_staff(webtest_staff):
    cs = ContentSetting.objects.get(name="REFFERAL_URL")

    resp = webtest_staff.get(
        f"/admin/content_settings/contentsetting/{cs.id}/history/", expect_errors=True
    )
    assert resp.status_int == 403


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_preview_on_site(webtest_admin, webtest_user, testadmin):
    us = UserPreview.objects.create(
        user=testadmin,
        name="TITLE",
        from_value="Book Store",
        value="New Title",
    )

    resp = webtest_user.get("/books/")
    assert resp.status_int == 200
    assert resp.html.find("title").text == "Book Store"

    resp = webtest_admin.get("/books/")
    assert resp.status_int == 200
    assert resp.html.find("title").text == "New Title"

    us.delete()

    resp = webtest_admin.get("/books/")
    assert resp.status_int == 200
    assert resp.html.find("title").text == "Book Store"


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_preview_on_site_see_the_preview(webtest_admin, testadmin):
    us = UserPreview.objects.create(
        user=testadmin,
        name="TITLE",
        from_value="Book Store",
        value="Supper New Title",
    )

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert b"Preview settings" in resp.content
    assert b"Supper New Title" in resp.content

    us.delete()
    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert b"Preview settings" not in resp.content
    assert b"Supper New Title" not in resp.content


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_preview_on_site_add_from_changelist(webtest_admin, testadmin):
    cs = ContentSetting.objects.all()[0]

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200

    assert resp.forms["changelist-form"]["form-0-value"].value == cs.value

    form = resp.forms["changelist-form"]
    form["form-0-value"] = "New Password"
    form["_preview_on_site"] = "on"
    resp = form.submit(name="_save")
    assert UserPreview.objects.all().count() == 1

    cs.refresh_from_db()
    assert cs.value == ""

    cs_preview = UserPreview.objects.all().first()
    assert cs_preview.name == cs.name
    assert cs_preview.from_value == cs.value
    assert cs_preview.value == "New Password"


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_preview_on_site_add_from_change_page(webtest_admin, testadmin):
    cs = ContentSetting.objects.all()[0]

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    assert resp.forms["contentsetting_form"]["value"].value == cs.value

    form = resp.forms["contentsetting_form"]
    form["value"] = "New Password"
    form["_preview_on_site"] = "on"
    form.submit()
    assert UserPreview.objects.all().count() == 1

    cs.refresh_from_db()
    assert cs.value == ""

    cs_preview = UserPreview.objects.all().first()
    assert cs_preview.name == cs.name
    assert cs_preview.from_value == cs.value
    assert cs_preview.value == "New Password"
    assert cs_preview.user == testadmin

    assert UserPreviewHistory.objects.all().count() == 1

    cs_preview_history = UserPreviewHistory.objects.all().first()
    assert cs_preview_history.name == cs.name
    assert cs_preview_history.value == "New Password"
    assert cs_preview_history.user == testadmin
    assert cs_preview_history.status == UserPreviewHistory.STATUS_CREATED


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_preview_on_site_add_from_change_page_update(webtest_admin, testadmin):
    cs = ContentSetting.objects.all()[0]

    UserPreview.objects.create(
        user=testadmin,
        name=cs.name,
        from_value=cs.value,
        value="New Password",
    )

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    assert resp.forms["contentsetting_form"]["value"].value == cs.value

    form = resp.forms["contentsetting_form"]
    form["value"] = "New Password2"
    form["_preview_on_site"] = "on"
    form.submit()
    assert UserPreview.objects.all().count() == 1
    assert UserPreviewHistory.objects.all().count() == 1

    cs_preview_history = UserPreviewHistory.objects.all().first()
    assert cs_preview_history.status == UserPreviewHistory.STATUS_CREATED


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_preview_on_site_applied(webtest_admin, testadmin):
    """
    Successfully applied preview, preview should be deleted, and the raw value of the setting should be updated
    """
    UserPreview.objects.create(
        user=testadmin,
        name="TITLE",
        from_value="Book Store",
        value="Supper New Title",
    )

    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/apply-preview-on-site/"
    )
    assert resp.status_int == 302

    assert UserPreview.objects.all().count() == 0
    assert ContentSetting.objects.get(name="TITLE").value == "Supper New Title"

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert extract_messages(resp) == ["Preview settings applied"]


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_admin_preview_on_site_applied_user_defined_type(webtest_admin, testadmin):
    """
    Successfully applied preview, preview should be deleted, and the raw value of the setting should be updated
    """
    UserPreview.objects.create(
        user=testadmin,
        name="CUSTOM_TITLE",
        value="Supper New Title",
        user_defined_type="line",
        tags="important",
        help="The Help",
    )

    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/apply-preview-on-site/"
    )
    assert resp.status_int == 302

    assert UserPreview.objects.all().count() == 0
    assert ContentSetting.objects.get(name="CUSTOM_TITLE").value == "Supper New Title"

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert extract_messages(resp) == ["Preview settings applied"]


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_admin_preview_on_site_applied_user_defined_type_update(
    webtest_admin, testadmin
):
    """
    Successfully applied preview, preview should be deleted, and the raw value of the setting should be updated
    """
    ContentSetting.objects.create(
        name="CUSTOM_TITLE",
        value="Old Title",
        user_defined_type="line",
        tags="important",
        help="The Help",
    )
    UserPreview.objects.create(
        user=testadmin,
        name="CUSTOM_TITLE",
        value="Supper New Title",
        from_value="Old Title",
        user_defined_type="line",
        from_user_defined_type="line",
        tags="important",
        from_tags="important",
        help="The Help",
        from_help="The Help",
    )

    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/apply-preview-on-site/"
    )
    assert resp.status_int == 302

    assert UserPreview.objects.all().count() == 0
    assert ContentSetting.objects.get(name="CUSTOM_TITLE").value == "Supper New Title"

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert extract_messages(resp) == ["Preview settings applied"]


def test_admin_preview_appliy_fail_no_preview(webtest_admin, testadmin):
    """
    Trying to apply preview when there is no preview settings
    """
    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/apply-preview-on-site/"
    )
    assert resp.status_int == 302

    assert UserPreview.objects.all().count() == 0

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert extract_messages(resp) == ["No preview settings to apply"]


def test_admin_preview_appliy_fail_validation(webtest_admin, testadmin):
    """
    Trying to apply preview when one of the previewed values is not valid
    """
    UserPreview.objects.create(
        user=testadmin,
        name="XARCHER_DEVIDER",
        from_value="10",
        value="ten",
    )

    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/apply-preview-on-site/"
    )
    assert resp.status_int == 302

    assert UserPreview.objects.all().count() == 1
    assert ContentSetting.objects.get(name="XARCHER_DEVIDER").value == "10"

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert extract_messages(resp) == ["XARCHER_DEVIDER: ['Enter a whole number.']"]


def test_admin_preview_appliy_fail_previous_doesnt_match(webtest_admin, testadmin):
    """
    Trying to apply preview when the setting was updated after the preview was added
    """
    UserPreview.objects.create(
        user=testadmin,
        name="XARCHER_DEVIDER",
        from_value="11",
        value="0",
    )

    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/apply-preview-on-site/"
    )
    assert resp.status_int == 302

    assert UserPreview.objects.all().count() == 1
    assert ContentSetting.objects.get(name="XARCHER_DEVIDER").value == "10"

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert extract_messages(resp) == [
        "The value XARCHER_DEVIDER was changed before applying the preview (check and apply again)"
    ]


def test_admin_preview_appliy_fail_previous_doesnt_match_but_ignored(
    webtest_admin, testadmin
):
    """
    Trying to apply preview when the setting was updated before to the value for the preview settings - in that case preview was removed
    """
    UserPreview.objects.create(
        user=testadmin,
        name="XARCHER_DEVIDER",
        from_value="11",
        value="10",
    )

    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/apply-preview-on-site/"
    )
    assert resp.status_int == 302

    assert UserPreview.objects.all().count() == 0
    assert ContentSetting.objects.get(name="XARCHER_DEVIDER").value == "10"

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert extract_messages(resp) == [
        "The value XARCHER_DEVIDER was changed already applied"
    ]


def test_admin_preview_appliy_fail_permission(webtest_staff, teststaff):
    """
    Trying to apply preview for staff user who doesn't have permissions to update XYARCHER_DEVIDER_SUPER
    """
    UserPreview.objects.create(
        user=teststaff,
        name="XYARCHER_DEVIDER_SUPER",
        from_value="10",
        value="0",
    )

    resp = webtest_staff.get(
        "/admin/content_settings/contentsetting/apply-preview-on-site/"
    )
    assert resp.status_int == 302

    assert UserPreview.objects.all().count() == 1
    assert ContentSetting.objects.get(name="XYARCHER_DEVIDER_SUPER").value == "10"

    resp = webtest_staff.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert extract_messages(resp) == [
        "You don't have permissions to update the setting XYARCHER_DEVIDER_SUPER"
    ]


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_preview_on_site_reset(webtest_admin, testadmin):
    UserPreview.objects.create(
        user=testadmin,
        name="TITLE",
        from_value="Book Store",
        value="Supper New Title",
    )

    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/reset-preview-on-site/"
    )
    assert resp.status_int == 302

    assert UserPreview.objects.all().count() == 0
    assert ContentSetting.objects.get(name="TITLE").value == "Book Store"


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_preview_on_site_remove(webtest_admin, testadmin):
    UserPreview.objects.create(
        user=testadmin,
        name="TITLE",
        from_value="Book Store",
        value="Supper New Title",
    )
    UserPreview.objects.create(
        user=testadmin,
        name="DESCRIPTION",
        from_value="Book Store",
        value="Supper New Description",
    )

    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/remove-preview-on-site/?name=TITLE"
    )
    assert resp.status_int == 302

    assert UserPreview.objects.all().count() == 1
    assert UserPreview.objects.all()[0].name == "DESCRIPTION"


@pytest.mark.skipif(
    not testing_settings_full, reason="skipping because of not testing_settings_full"
)
def test_add_user_defined_variable(webtest_admin, testadmin):
    resp = webtest_admin.get("/admin/content_settings/contentsetting/add/")

    form = resp.forms["contentsetting_form"]
    form["name"] = "NEW_VARIABLE"
    form["value"] = "New Value"
    form["user_defined_type"] = "text"
    form["help"] = "The Help"
    form["tags"] = "prof_email"

    resp = form.submit(name="_save")
    cs = ContentSetting.objects.get(name="NEW_VARIABLE")
    assert cs.value == "New Value"
    assert cs.user_defined_type == "text"
    assert cs.help == "The Help"
    assert cs.tags == "prof_email"

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200
    form = resp.forms["contentsetting_form"]

    assert form["name"].value == "NEW_VARIABLE"
    assert form["value"].value == "New Value"
    assert form["user_defined_type"].value == "text"
    assert form["help"].value == "The Help"
    assert form["tags"].value == "prof_email"


@pytest.mark.skipif(
    not testing_settings_full, reason="skipping because of not testing_settings_full"
)
def test_edit_user_defined_variable(webtest_admin, testadmin):
    cs = ContentSetting.objects.create(
        name="NEW_VARIABLE",
        value="New Value",
        user_defined_type="text",
        help="The Help",
        tags="prof_email",
    )
    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    form = resp.forms["contentsetting_form"]
    assert form["tags"].value == "prof_email"

    form["tags"] = "next_email"
    resp = form.submit(name="_save")

    cs.refresh_from_db()
    assert cs.tags == "next_email"


def test_admin_head(webtest_admin):

    cs = ContentSetting.objects.get(name="TITLE")
    URLS = [
        f"/admin/content_settings/contentsetting/{cs.id}/change/",
        f"/admin/content_settings/contentsetting/",
    ]
    if testing_settings_full:
        URLS.append(f"/admin/content_settings/contentsetting/add/")

    for url in URLS:
        resp = webtest_admin.get(url)

        assert resp.status_int == 200

        assert "simple-line-icons.min.css" in resp.content.decode("utf-8")
        assert resp.content.decode("utf-8").count("simple-line-icons.min.css") == 1
        assert "simple-line-icons.min.js" in resp.content.decode("utf-8")
        assert resp.content.decode("utf-8").count("simple-line-icons.min.js") == 1
        assert ".some_block_css" in resp.content.decode("utf-8")
        assert resp.content.decode("utf-8").count(".some_block_css") == 1
        assert 'console.log("Hello, ADMIN HEAD JS");' in resp.content.decode("utf-8")
        assert (
            resp.content.decode("utf-8").count('console.log("Hello, ADMIN HEAD JS");')
            == 1
        )


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_changelist_changechain_valid(webtest_admin, testadmin):
    """
    (changelist interface)
    we have 3 variables:
    XARCHER_DEVIDER -> YARCHER_DEVIDER -> XSHOT_CALCULATION

    by changing XARCHER_DEVIDER to 1 we should have no validation error for variable XSHOT_CALCULATION
    """

    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/?q=XARCHER_DEVIDER"
    )
    assert resp.status_int == 200

    form = resp.forms["changelist-form"]
    form["form-0-value"] = "1"
    resp = form.submit(name="_save")

    assert resp.status_int == 302


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_changelist_changechain_to_zero(webtest_admin, testadmin):
    """
    (changelist interface)
    we have 3 variables:
    XARCHER_DEVIDER -> YARCHER_DEVIDER -> XSHOT_CALCULATION

    by changing XARCHER_DEVIDER to 0 we should have a validation error for variable XSHOT_CALCULATION
    """

    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/?q=XARCHER_DEVIDER"
    )
    assert resp.status_int == 200
    form = resp.forms["changelist-form"]
    form["form-0-value"] = "0"
    resp = form.submit(name="_save")

    assert resp.status_int == 200
    assert b"Error validating XSHOT_CALCULATION:" in resp.content


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_single_changechain_valid(webtest_admin, testadmin):
    """
    (single change interface)
    we have 3 variables:
    XARCHER_DEVIDER -> YARCHER_DEVIDER -> XSHOT_CALCULATION

    by changing XARCHER_DEVIDER to 1 we should have no validation error for variable XSHOT_CALCULATION
    """

    cs = ContentSetting.objects.get(name="XARCHER_DEVIDER")

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    form = resp.forms["contentsetting_form"]
    form["value"] = "1"
    resp = form.submit(name="_save")

    assert resp.status_int == 302
    cs.refresh_from_db()
    assert cs.value == "1"


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_single_changechain_to_zero(webtest_admin, testadmin):
    """
    (single change interface)
    we have 3 variables:
    XARCHER_DEVIDER -> YARCHER_DEVIDER -> XSHOT_CALCULATION

    by changing XARCHER_DEVIDER to 0 we should have a validation error for variable XSHOT_CALCULATION
    """

    cs = ContentSetting.objects.get(name="XARCHER_DEVIDER")

    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/change/")
    assert resp.status_int == 200

    form = resp.forms["contentsetting_form"]
    form["value"] = "0"
    resp = form.submit(name="_save")

    assert resp.status_int == 200
    assert resp.context["errors"] == [
        ["Error validating XSHOT_CALCULATION: ['division by zero']"]
    ]
    cs.refresh_from_db()
    assert cs.value == "10"


@pytest.mark.skipif(
    testing_settings_min, reason="skipping because of testing_settings_min"
)
def test_admin_preview_appliy_fail_chained(webtest_admin, testadmin):
    """
    Trying to apply preview for XARCHER_DEVIDER if it has a chain reaction to XSHOT_CALCULATION so the value wasn't applied
    """
    UserPreview.objects.create(
        user=testadmin,
        name="XARCHER_DEVIDER",
        from_value="10",
        value="0",
    )

    resp = webtest_admin.get(
        "/admin/content_settings/contentsetting/apply-preview-on-site/"
    )
    assert resp.status_int == 302

    assert UserPreview.objects.all().count() == 1
    assert ContentSetting.objects.get(name="XARCHER_DEVIDER").value == "10"

    resp = webtest_admin.get("/admin/content_settings/contentsetting/")
    assert resp.status_int == 200
    assert extract_messages(resp) == [
        "[\"Error validating XSHOT_CALCULATION: ['division by zero']\"]"
    ]
