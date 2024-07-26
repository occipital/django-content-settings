import pytest
import json

from content_settings.models import ContentSetting, UserPreview

from tests import testing_settings_min, testing_settings_full

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_not_valid_json(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {"raw_json": "not valid json"},
    )

    assert resp.status_int == 200
    assert b"Error JSON parsing" in resp.body


def test_wrong_format(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"bla": {"XARCHER_DEVIDER": {"value": "10", "version": ""}}}
            )
        },
    )

    assert resp.status_int == 200

    assert b"Wrong JSON format. Settings should be set" in resp.body


def test_wrong_format_settings_dict(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {"raw_json": json.dumps({"settings": ["XARCHER_DEVIDER"]})},
    )

    assert resp.status_int == 200

    assert b"Wrong JSON format. Settings should be a dictionary" in resp.body


def test_value_is_the_same(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "10", "version": ""}}}
            )
        },
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == [
        {"name": "XARCHER_DEVIDER", "reason": "Value is the same"}
    ]
    assert resp.context["applied"] == []
    assert resp.context["errors"] == []


def test_value_is_not_set(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {"raw_json": json.dumps({"settings": {"XARCHER_DEVIDER": {"version": "old"}}})},
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == []
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "XARCHER_DEVIDER", "reason": "Value is not set or not a string"}
    ]


def test_value_is_not_string(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": 1, "version": ""}}}
            )
        },
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == []
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "XARCHER_DEVIDER", "reason": "Value is not set or not a string"}
    ]


def test_version_is_not_set(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {"raw_json": json.dumps({"settings": {"XARCHER_DEVIDER": {"value": "1"}}})},
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == []
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "XARCHER_DEVIDER", "reason": "Version is not set or not a string"}
    ]


def test_version_is_not_string(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "1", "version": 1}}}
            )
        },
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == []
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "XARCHER_DEVIDER", "reason": "Version is not set or not a string"}
    ]


def test_version_is_not_the_save(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "1", "version": "old"}}}
            )
        },
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == []
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "XARCHER_DEVIDER", "reason": "Version is not the same"}
    ]


def test_setting_does_not_exist(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_OLD": {"value": "1", "version": ""}}}
            )
        },
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == []
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "XARCHER_OLD", "reason": "Setting does not exist"}
    ]


def test_not_valid(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "zero", "version": ""}}}
            )
        },
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == []
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "XARCHER_DEVIDER", "reason": "['Enter a whole number.']"}
    ]


def test_value_permissions(webtest_staff):
    resp = webtest_staff.post(
        "/admin/content_settings/contentsetting/import-json/",
        {"raw_json": json.dumps({"settings": {"BOOKS": {"value": "", "version": ""}}})},
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == []
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "BOOKS", "reason": "You don't have permissions to update the setting"}
    ]


def test_value_applied(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "9", "version": ""}}}
            )
        },
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == []
    assert resp.context["applied"] == [
        {"name": "XARCHER_DEVIDER", "old_value": "10", "new_value": "9"}
    ]
    assert resp.context["errors"] == []


def test_value_imported(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "9", "version": ""}}}
            ),
            "_applied": ["XARCHER_DEVIDER"],
            "_import": "Import",
        },
    )

    assert resp.status_int == 302
    assert resp.location.endswith("/admin/content_settings/contentsetting/")
    assert ContentSetting.objects.get(name="XARCHER_DEVIDER").value == "9"


@pytest.mark.skipif(
    testing_settings_min, reason="Only for non minimal testing settings"
)
def test_value_imported_preview(webtest_admin, testadmin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "9", "version": ""}}}
            ),
            "_applied": ["XARCHER_DEVIDER"],
            "_import": "Import",
            "preview_on_site": "1",
        },
    )

    assert resp.status_int == 302
    assert resp.location.endswith("/admin/content_settings/contentsetting/")
    assert ContentSetting.objects.get(name="XARCHER_DEVIDER").value == "10"
    assert UserPreview.objects.filter(user=testadmin, name="XARCHER_DEVIDER").exists()


@pytest.mark.skipif(
    testing_settings_min, reason="Only for non minimal testing settings"
)
def test_value_imported_preview_is_not_allowed(webtest_staff):
    resp = webtest_staff.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "9", "version": ""}}}
            ),
            "_applied": ["XARCHER_DEVIDER"],
            "_import": "Import",
            "preview_on_site": "1",
        },
    )

    assert resp.status_int == 200
    assert b"You don&#x27;t have permissions to apply preview on site." in resp.content


@pytest.mark.skipif(
    testing_settings_min, reason="Only for non minimal testing settings"
)
def test_see_preview_on_site(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "9", "version": ""}}}
            ),
        },
    )

    assert resp.status_int == 200
    assert b"Preview on Site" in resp.content


@pytest.mark.skipif(
    not testing_settings_min, reason="Only for minimal testing settings"
)
def test_not_see_preview_on_site_for_minimal(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "9", "version": ""}}}
            ),
        },
    )

    assert resp.status_int == 200
    assert b"Preview on Site" not in resp.content


@pytest.mark.skipif(
    testing_settings_min, reason="Only for non minimal testing settings"
)
def test_not_see_preview_on_site_for_staff(webtest_staff):
    resp = webtest_staff.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "9", "version": ""}}}
            ),
        },
    )

    assert resp.status_int == 200
    assert b"Preview on Site" not in resp.content


@pytest.mark.skipif(
    testing_settings_min, reason="Only for non minimal testing settings"
)
def test_prevent_chain_import(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "0", "version": ""}}}
            ),
            "_applied": ["XARCHER_DEVIDER"],
            "_import": "Import",
        },
    )

    assert resp.status_int == 200
    assert b"Error validating XSHOT_CALCULATION" in resp.content


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_prevent_checksum_import(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "9", "version": ""}}}
            ),
            "_applied": ["XARCHER_DEVIDER"],
            "_import": "Import",
            "content_settings_full_checksum": "wrong",
        },
    )

    assert resp.status_int == 200
    assert b"The content settings have been changed by another user." in resp.content


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_checksum_import(webtest_admin):
    from content_settings.conf import content_settings

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "9", "version": ""}}}
            ),
            "_applied": ["XARCHER_DEVIDER"],
            "_import": "Import",
            "content_settings_full_checksum": content_settings.full_checksum,
        },
    )

    assert resp.status_int == 302
    assert resp.location.endswith("/admin/content_settings/contentsetting/")
    assert ContentSetting.objects.get(name="XARCHER_DEVIDER").value == "9"


# TODO Export:
# TODO Import:
# no permissions
# file not valid
# the value is not valid
# admin checksum is changed
# submit in preview
# submit in value
# preview on site should not be shown for minimal settings
