import pytest

from django.test import Client
from django.contrib.auth import get_user_model

from content_settings.models import ContentSetting
from content_settings.context_managers import content_settings_context
from content_settings.types.template import DjangoTemplateNoArgs
from content_settings.caching import check_update, recalc_checksums
from content_settings.conf import set_initial_values_for_db

pytestmark = [pytest.mark.django_db(transaction=True)]


def create_content_settings(**kwargs):

    return ContentSetting.objects.create(**kwargs)


def test_simple():
    create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )
    client = Client()
    resp = client.get("/content-settings/fetch/prefix/")
    assert resp.status_code == 200
    assert resp.json() == {"PREFIX": "Some Title Prefix"}


def test_simple_update_value():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )
    client = Client()
    resp = client.get("/content-settings/fetch/prefix/")
    assert resp.status_code == 200
    assert resp.json() == {"PREFIX": "Some Title Prefix"}

    cs.value = "New Title Prefix"
    cs.save()
    resp = client.get("/content-settings/fetch/prefix/")
    assert resp.status_code == 200
    assert resp.json() == {"PREFIX": "New Title Prefix"}


def test_simple_remove_value():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )
    client = Client()
    resp = client.get("/content-settings/fetch/prefix/")
    assert resp.status_code == 200
    assert resp.json() == {"PREFIX": "Some Title Prefix"}

    cs.delete()
    resp = client.get("/content-settings/fetch/prefix/")
    assert resp.status_code == 404


def test_simple_update_name():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )
    client = Client()
    resp = client.get("/content-settings/fetch/prefix/")
    assert resp.status_code == 200
    assert resp.json() == {"PREFIX": "Some Title Prefix"}

    cs.name = "PREFIX_UPDATED"
    cs.save()
    resp = client.get("/content-settings/fetch/prefix/")
    assert resp.status_code == 404

    resp = client.get("/content-settings/fetch/prefix-updated/")
    assert resp.status_code == 200
    assert resp.json() == {"PREFIX_UPDATED": "Some Title Prefix"}


def test_simple_update_version():
    cs = create_content_settings(
        name="PREFIX",
        value="Some Title Prefix",
        user_defined_type="line",
    )
    client = Client()
    resp = client.get("/content-settings/fetch/prefix/")
    assert resp.status_code == 200
    assert resp.json() == {"PREFIX": "Some Title Prefix"}

    ContentSetting.objects.filter(name="PREFIX").update(
        version=cs.version + "1", value="New Prefix"
    )
    recalc_checksums()

    resp = client.get("/content-settings/fetch/prefix/")
    assert resp.status_code == 200
    assert resp.json() == {"PREFIX": "Some Title Prefix"}


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
    cs.user_defined_type = "unknown"
    cs.save()

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
    resp = client.get("/content-settings/fetch/custom-title/")
    assert resp.status_code == 200
    assert resp.json() == {"CUSTOM_TITLE": "My Way"}
