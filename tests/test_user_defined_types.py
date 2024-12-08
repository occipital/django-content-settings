import pytest
import re

from django.test import Client

from content_settings.models import ContentSetting, UserPreview
from content_settings.types.template import DjangoTemplateNoArgs
from content_settings.caching import check_update, recalc_checksums
from content_settings.conf import set_initial_values_for_db

from tests import testing_settings_full

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.skipif(
        not testing_settings_full,
        reason="skipping because of not testing_settings_full",
    ),
]


def create_content_settings(**kwargs):

    return ContentSetting.objects.create(**kwargs)


def test_simple():
    create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )
    client = Client()

    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["PREFIX"] == "Some Title Prefix"


def test_simple_update_value():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )
    client = Client()
    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["PREFIX"] == "Some Title Prefix"

    cs.value = "New Title Prefix"
    cs.save()
    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["PREFIX"] == "New Title Prefix"


def test_simple_remove_value():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )
    client = Client()
    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["PREFIX"] == "Some Title Prefix"

    cs.delete()
    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert "PREFIX" not in resp.json()


def test_simple_update_name():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )
    client = Client()
    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["PREFIX"] == "Some Title Prefix"

    cs.name = "PREFIX_UPDATED"
    cs.save()

    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["PREFIX_UPDATED"] == "Some Title Prefix"
    assert "PREFIX" not in resp.json()


def test_simple_update_version():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )
    client = Client()
    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["PREFIX"] == "Some Title Prefix"

    ContentSetting.objects.filter(name="PREFIX").update(
        version=cs.version + "1", value="New Prefix"
    )
    recalc_checksums()

    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["PREFIX"] == "Some Title Prefix"


def test_simple_in_other_var():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )

    check_update()

    var = DjangoTemplateNoArgs()
    assert (
        var.give_python("{{CONTENT_SETTINGS.PREFIX}} TITLE")
        == "Some Title Prefix TITLE"
    )

    cs.delete()

    check_update()
    assert var.give_python("{{CONTENT_SETTINGS.PREFIX}} TITLE") == " TITLE"


def test_initial_simple():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )

    assert set_initial_values_for_db() == []


def test_reset_default():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )

    ContentSetting.objects.filter(name="PREFIX").update(version=cs.version + "1")
    recalc_checksums()

    assert set_initial_values_for_db(apply=True) == [("PREFIX", "update")]

    cs.refresh_from_db()
    assert cs.value == ""


def test_reset_unknown_type():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )
    ContentSetting.objects.filter(name="PREFIX").update(user_defined_type="unknown")

    assert set_initial_values_for_db(apply=True) == [("PREFIX", "delete")]


def test_preview_simple(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "PREFIX",
            "value": "New Title",
            "user_defined_type": "line",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {"html": ""}


def test_preview_simple_html(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/preview/",
        {
            "name": "PREFIX",
            "value": "New Title",
            "user_defined_type": "html",
        },
    )

    assert resp.status_int == 200
    assert resp.json == {"html": "New Title"}


def test_admin_add(webtest_admin):
    resp = webtest_admin.get("/admin/content_settings/contentsetting/add/")
    assert resp.status_int == 200
    resp.forms["contentsetting_form"]["name"] = "CUSTOM_TITLE"
    resp.forms["contentsetting_form"]["value"] = "My Way"
    resp.forms["contentsetting_form"]["user_defined_type"] = "line"
    resp = resp.forms["contentsetting_form"].submit()
    assert resp.status_int == 302

    cs = ContentSetting.objects.get(name="CUSTOM_TITLE")
    assert cs.version == "3.0.0"

    client = Client()
    resp = client.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json()["CUSTOM_TITLE"] == "My Way"


def test_admin_add_preview(webtest_admin, testadmin):
    resp = webtest_admin.get("/admin/content_settings/contentsetting/add/")
    assert resp.status_int == 200
    resp.forms["contentsetting_form"]["name"] = "CUSTOM_TITLE"
    resp.forms["contentsetting_form"]["value"] = "My Way"
    resp.forms["contentsetting_form"]["user_defined_type"] = "line"
    resp.forms["contentsetting_form"]["_preview_on_site"] = "on"
    resp = resp.forms["contentsetting_form"].submit()
    assert resp.status_int == 302

    assert ContentSetting.objects.filter(name="CUSTOM_TITLE").count() == 0
    assert UserPreview.objects.filter(user=testadmin, name="CUSTOM_TITLE").count() == 1

    resp = webtest_admin.get("/books/fetch/all/")
    assert resp.status_code == 200
    assert resp.json["CUSTOM_TITLE"] == "My Way"


def test_admin_update_history(webtest_admin):
    resp = webtest_admin.get("/admin/content_settings/contentsetting/add/")
    assert resp.status_int == 200
    resp.forms["contentsetting_form"]["name"] = "CUSTOM_TITLE"
    resp.forms["contentsetting_form"]["value"] = "My Way"
    resp.forms["contentsetting_form"]["user_defined_type"] = "line"
    resp = resp.forms["contentsetting_form"].submit()

    cs = ContentSetting.objects.get(name="CUSTOM_TITLE")
    resp = webtest_admin.get(f"/admin/content_settings/contentsetting/{cs.id}/history/")
    assert resp.status_int == 200
    assert len(resp.html.find("table", {"id": "change-history"}).find_all("tr")) == 2

    assert (
        re.sub(
            r"\s+",
            " ",
            resp.html.find("table", {"id": "change-history"})
            .find_all("tr")[1]
            .find_all("td")[0]
            .text.replace("\n", " "),
        ).strip()
        == "Added by user testadmin"
    )


def test_fetch_tags():
    client = Client()
    resp = client.get("/books/fetch/general/")
    assert resp.json() == {
        "DESCRIPTION": "Book Store is the best book store in the world",
        "TITLE": "Book Store",
    }

    create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
        tags="general",
    )

    # wrong tag
    create_content_settings(
        name="PREFIX2",
        value="Some Title Prefix",
        user_defined_type="line",
        tags="general2",
    )

    # no permissions
    create_content_settings(
        name="PREFIX3",
        value="Some Title Prefix",
        user_defined_type="text",
        tags="general",
    )

    resp = client.get("/books/fetch/general/")
    assert resp.json() == {
        "DESCRIPTION": "Book Store is the best book store in the world",
        "TITLE": "Book Store",
        "PREFIX": "Some Title Prefix",
    }


def test_fetch_startswith():
    client = Client()
    resp = client.get("/books/fetch/is/")
    assert resp.json() == {"IS_CLOSED": False}

    create_content_settings(
        name="IS_EXISITNG",
        value="Some Title Prefix",
        user_defined_type="line",
    )

    # we looking for only "IS_" prefix
    create_content_settings(
        name="ISTANBUL",
        value="Some Title Prefix",
        user_defined_type="line",
    )

    resp = client.get("/books/fetch/is/")
    assert resp.json() == {"IS_CLOSED": False, "IS_EXISITNG": "Some Title Prefix"}
