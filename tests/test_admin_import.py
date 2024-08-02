import pytest
import json

from content_settings.models import ContentSetting, UserPreview

from tests import testing_settings_min, testing_settings_full

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_not_valid_json(webtest_admin):
    """Test that submitting invalid JSON returns an error message."""
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {"raw_json": "not valid json"},
    )

    assert resp.status_int == 200
    assert b"Error JSON parsing" in resp.body


def test_wrong_format(webtest_admin):
    """Test that submitting JSON with incorrect top-level structure returns an error."""
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
    """Test that submitting settings as a list instead of a dictionary returns an error."""
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {"raw_json": json.dumps({"settings": ["XARCHER_DEVIDER"]})},
    )

    assert resp.status_int == 200

    assert b"Wrong JSON format. Settings should be a dictionary" in resp.body


def test_value_is_the_same(webtest_admin):
    """Test that submitting a setting with the same value as existing is skipped."""
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
    """Test that submitting a setting without a 'value' field returns an error."""
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {"raw_json": json.dumps({"settings": {"XARCHER_DEVIDER": {"version": "old"}}})},
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == []
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "XARCHER_DEVIDER", "reason": '"value" is not set or not a string'}
    ]


def test_value_is_not_string(webtest_admin):
    """Test that submitting a non-string value for a setting returns an error."""
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
        {"name": "XARCHER_DEVIDER", "reason": '"value" is not set or not a string'}
    ]


def test_version_is_not_set(webtest_admin):
    """Test that submitting a setting without a 'version' field returns an error."""
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {"raw_json": json.dumps({"settings": {"XARCHER_DEVIDER": {"value": "1"}}})},
    )

    assert resp.status_int == 200
    assert resp.context["skipped"] == []
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "XARCHER_DEVIDER", "reason": '"version" is not set or not a string'}
    ]


def test_version_is_not_string(webtest_admin):
    """Test that submitting a non-string version for a setting returns an error."""
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
        {"name": "XARCHER_DEVIDER", "reason": '"version" is not set or not a string'}
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
        {
            "name": "XARCHER_DEVIDER",
            "old_value": "10",
            "new_value": "9",
            "full": {"value": "9"},
        }
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


def test_value_imported_not_applied(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "9", "version": ""}}}
            ),
            "_applied": [],
            "_import": "Import",
        },
    )

    assert resp.status_int == 302
    assert resp.location.endswith("/admin/content_settings/contentsetting/")
    assert ContentSetting.objects.get(name="XARCHER_DEVIDER").value == "10"


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
def test_value_imported_preview_not_applied(webtest_admin, testadmin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {"settings": {"XARCHER_DEVIDER": {"value": "9", "version": ""}}}
            ),
            "_applied": [],
            "_import": "Import",
            "preview_on_site": "1",
        },
    )

    assert resp.status_int == 302
    assert resp.location.endswith("/admin/content_settings/contentsetting/")
    assert ContentSetting.objects.get(name="XARCHER_DEVIDER").value == "10"
    assert not UserPreview.objects.filter(
        user=testadmin, name="XARCHER_DEVIDER"
    ).exists()


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


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_applied(webtest_admin):
    from content_settings.conf import content_settings

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "1",
                            "tags": "",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "content_settings_full_checksum": content_settings.full_checksum,
        },
    )

    assert resp.status_int == 200
    assert resp.context["applied"] == [
        {
            "name": "GIG",
            "new_value": {
                "value": "1",
                "tags": "",
                "help": "",
                "version": "",
                "user_defined_type": "bool",
            },
            "full": {
                "value": "1",
                "tags": "",
                "help": "",
                "version": "",
                "user_defined_type": "bool",
            },
        }
    ]


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_applied_update(webtest_admin):
    from content_settings.conf import content_settings

    ContentSetting.objects.create(
        name="GIG", value="0", tags="", help="", version="", user_defined_type="bool"
    )

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "1",
                            "tags": "",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "content_settings_full_checksum": content_settings.full_checksum,
        },
    )

    assert resp.status_int == 200
    assert resp.context["applied"] == [
        {
            "name": "GIG",
            "old_value": {"value": "0"},
            "new_value": {"value": "1"},
            "full": {
                "value": "1",
                "tags": "",
                "help": "",
                "version": "",
                "user_defined_type": "bool",
            },
        }
    ]


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_skiped(webtest_admin):
    from content_settings.conf import content_settings

    ContentSetting.objects.create(
        name="GIG", value="1", tags="", help="", version="", user_defined_type="bool"
    )

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "1",
                            "tags": "",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "content_settings_full_checksum": content_settings.full_checksum,
        },
    )

    assert resp.status_int == 200
    assert resp.context["applied"] == []
    assert resp.context["skipped"] == [{"name": "GIG", "reason": "Value is the same"}]


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_applied_update_tags(webtest_admin):
    from content_settings.conf import content_settings

    ContentSetting.objects.create(
        name="GIG",
        value="0",
        tags="general",
        help="",
        version="",
        user_defined_type="bool",
    )

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "1",
                            "tags": "new",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "content_settings_full_checksum": content_settings.full_checksum,
        },
    )

    assert resp.status_int == 200
    assert resp.context["applied"] == [
        {
            "name": "GIG",
            "old_value": {"value": "0", "tags": "general"},
            "new_value": {"value": "1", "tags": "new"},
            "full": {
                "value": "1",
                "tags": "new",
                "help": "",
                "version": "",
                "user_defined_type": "bool",
            },
        }
    ]


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_skiped_tags(webtest_admin):
    from content_settings.conf import content_settings

    ContentSetting.objects.create(
        name="GIG",
        value="1",
        tags="general\nnew",
        help="",
        version="",
        user_defined_type="bool",
    )

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "1",
                            "tags": "new\ngeneral",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "content_settings_full_checksum": content_settings.full_checksum,
        },
    )

    assert resp.status_int == 200
    assert resp.context["applied"] == []
    assert resp.context["skipped"] == [{"name": "GIG", "reason": "Value is the same"}]


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_error_validated(webtest_admin):
    from content_settings.conf import content_settings

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "uno",
                            "tags": "",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "content_settings_full_checksum": content_settings.full_checksum,
        },
    )

    assert resp.status_int == 200
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {
            "name": "GIG",
            "reason": "[\"Value cannot be 'yes', 'true', '1', '+', 'ok', 'no', 'not', 'false', '0', '-', empty only\"]",
        }
    ]


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_error_wrong_type(webtest_admin):
    from content_settings.conf import content_settings

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "uno",
                            "tags": "",
                            "help": "",
                            "version": "",
                            "user_defined_type": "float",
                        }
                    }
                }
            ),
            "content_settings_full_checksum": content_settings.full_checksum,
        },
    )

    assert resp.status_int == 200
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "GIG", "reason": "Invalid user_defined_type"}
    ]


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_error_invalid_format(webtest_admin):
    from content_settings.conf import content_settings

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "tags": "",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "content_settings_full_checksum": content_settings.full_checksum,
        },
    )

    assert resp.status_int == 200
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "GIG", "reason": '"value" is not set or not a string'}
    ]


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_error_invalid_format_int(webtest_admin):
    from content_settings.conf import content_settings

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": 1,
                            "tags": "",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "content_settings_full_checksum": content_settings.full_checksum,
        },
    )

    assert resp.status_int == 200
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [
        {"name": "GIG", "reason": '"value" is not set or not a string'}
    ]


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_error_invalid_version(webtest_admin):
    from content_settings.conf import content_settings

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "1",
                            "tags": "",
                            "help": "",
                            "version": "1",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "content_settings_full_checksum": content_settings.full_checksum,
        },
    )

    assert resp.status_int == 200
    assert resp.context["applied"] == []
    assert resp.context["errors"] == [{"name": "GIG", "reason": "Invalid version"}]


@pytest.mark.skipif(testing_settings_min, reason="Only for non min testing settings")
def test_prevent_chain_import_with_userdefined(webtest_admin):
    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "XARCHER_DEVIDER": {"value": "0", "version": ""},
                        "GIG": {
                            "value": "1",
                            "tags": "",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        },
                    }
                }
            ),
            "_applied": ["XARCHER_DEVIDER"],
            "_import": "Import",
        },
    )

    assert resp.status_int == 200
    assert b"Error validating XSHOT_CALCULATION" in resp.content


@pytest.mark.skipif(testing_settings_min, reason="Only for non min testing settings")
def test_prevent_chain_import_with_userdefined_updated(webtest_admin):
    ContentSetting.objects.create(
        name="GIG", value="0", tags="", help="", version="", user_defined_type="bool"
    )

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "XARCHER_DEVIDER": {"value": "0", "version": ""},
                        "GIG": {
                            "value": "1",
                            "tags": "",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        },
                    }
                }
            ),
            "_applied": ["XARCHER_DEVIDER"],
            "_import": "Import",
        },
    )

    assert resp.status_int == 200
    assert b"Error validating XSHOT_CALCULATION" in resp.content


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_added(webtest_admin):
    from content_settings.conf import content_settings

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "1",
                            "tags": "new",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "_applied": ["GIG"],
            "_import": "Import",
        },
    )

    assert resp.status_int == 302
    assert resp.location.endswith("/admin/content_settings/contentsetting/")

    cs = ContentSetting.objects.get(name="GIG")
    assert cs.value == "1"
    assert cs.tags == "new"
    assert cs.help == ""
    assert cs.version == ""
    assert cs.user_defined_type == "bool"


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_added_updated(webtest_admin):

    cs = ContentSetting.objects.create(
        name="GIG", value="0", tags="", help="", version="", user_defined_type="bool"
    )

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "1",
                            "tags": "new",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "_applied": ["GIG"],
            "_import": "Import",
        },
    )

    assert resp.status_int == 302
    assert resp.location.endswith("/admin/content_settings/contentsetting/")

    cs.refresh_from_db()
    assert cs.value == "1"
    assert cs.tags == "new"
    assert cs.help == ""
    assert cs.version == ""
    assert cs.user_defined_type == "bool"


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_added_to_preview(webtest_admin, testadmin):

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "1",
                            "tags": "new",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "_applied": ["GIG"],
            "_import": "Import",
            "preview_on_site": "1",
        },
    )

    assert resp.status_int == 302
    assert resp.location.endswith("/admin/content_settings/contentsetting/")

    up = UserPreview.objects.get(name="GIG", user=testadmin)
    assert up.value == "1"
    assert up.tags == "new"
    assert up.help == ""
    assert up.user_defined_type == "bool"


@pytest.mark.skipif(not testing_settings_full, reason="Only for full testing settings")
def test_userdeined_added_update_to_preview(webtest_admin, testadmin):

    up = UserPreview.objects.create(
        name="GIG",
        user=testadmin,
        value="0",
        tags="",
        help="",
        user_defined_type="bool",
    )

    resp = webtest_admin.post(
        "/admin/content_settings/contentsetting/import-json/",
        {
            "raw_json": json.dumps(
                {
                    "settings": {
                        "GIG": {
                            "value": "1",
                            "tags": "new",
                            "help": "",
                            "version": "",
                            "user_defined_type": "bool",
                        }
                    }
                }
            ),
            "_applied": ["GIG"],
            "_import": "Import",
            "preview_on_site": "1",
        },
    )

    assert resp.status_int == 302
    assert resp.location.endswith("/admin/content_settings/contentsetting/")

    up.refresh_from_db()
    assert up.value == "1"
    assert up.tags == "new"
    assert up.help == ""
    assert up.user_defined_type == "bool"
