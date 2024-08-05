import pytest
import json
from io import StringIO
import os

from django.core.management import call_command

from content_settings.models import ContentSetting, UserPreview

pytestmark = [pytest.mark.django_db(transaction=True)]


def std_command(command, *args, **kwargs):
    out = StringIO()
    err = StringIO()
    call_command(command, *args, stdout=out, stderr=err, **kwargs)
    return out.getvalue(), err.getvalue()


def std_import(data, *args, **kwargs):
    import tempfile

    # Create a temporary file
    with tempfile.NamedTemporaryFile(
        mode="w+", delete=False, suffix=".json"
    ) as tmp_file:
        # Write the data to the temporary file
        json.dump(data, tmp_file)
        tmp_file.flush()

    # Call the import command with the temporary file
    try:
        return std_command("content_settings_import", tmp_file.name, *args, **kwargs)
    finally:
        os.unlink(tmp_file.name)


def test_export_all():

    # Call the command
    out, err = std_command("content_settings_export")

    # Check that there's no stderr output
    assert not err, "Expected no stderr output"

    # Check that stdout is JSON serializable
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        pytest.fail("Stdout is not JSON serializable")
    else:
        assert data["settings"]


def test_export_names():
    out, err = std_command(
        "content_settings_export", "--names", "TITLE", "BOOKS_ON_HOME_PAGE"
    )
    assert not err, "Expected no stderr output"
    assert json.loads(out)["settings"] == {
        "BOOKS_ON_HOME_PAGE": {"value": "3", "version": ""},
        "TITLE": {"value": "Book Store", "version": ""},
    }


def test_import_one_setting():
    out, err = std_import(
        {
            "settings": {
                "TITLE": {"value": "The New Book Store", "version": ""},
            }
        },
    )
    assert not err, "Expected no stderr output"
    assert "Applied" in out
    assert ContentSetting.objects.get(name="TITLE").value == "Book Store"


def test_import_one_setting_error():
    out, err = std_import(
        {
            "settings": {
                "TITLE": {"value": "The New Book Store", "version": "2"},
            }
        },
    )
    assert err
    assert "Applied" not in out
    assert ContentSetting.objects.get(name="TITLE").value == "Book Store"


def test_import_one_setting_preview(teststaff):
    out, err = std_import(
        {
            "settings": {
                "TITLE": {"value": "The New Book Store", "version": ""},
            }
        },
        preview_for="teststaff",
    )
    assert not err
    assert "Applied" in out
    assert ContentSetting.objects.get(name="TITLE").value == "Book Store"
    assert (
        UserPreview.objects.get(user=teststaff, name="TITLE").value
        == "The New Book Store"
    )


def test_import_one_setting_confirmed(teststaff):
    out, err = std_import(
        {
            "settings": {
                "TITLE": {"value": "The New Book Store", "version": ""},
            }
        },
        "--import",
    )
    assert not err
    assert "Applied" in out
    assert ContentSetting.objects.get(name="TITLE").value == "The New Book Store"


def test_import_two_settings_one_error():
    out, err = std_import(
        {
            "settings": {
                "TITLE": {"value": "The New Book Store", "version": "2"},
                "BOOKS_ON_HOME_PAGE": {"value": "4", "version": ""},
            }
        },
    )
    assert err
    assert "Applied" in out


def test_import_two_settings_show_only_errors():
    out, err = std_import(
        {
            "settings": {
                "TITLE": {"value": "The New Book Store", "version": "2"},
                "BOOKS_ON_HOME_PAGE": {"value": "4", "version": ""},
            }
        },
        "--show-only-errors",
    )
    assert err
    assert "Applied" not in out


def test_import_two_settings_not_show_skipped():
    out, err = std_import(
        {
            "settings": {
                "TITLE": {"value": "The New Book Store", "version": "2"},
                "BOOKS_ON_HOME_PAGE": {"value": "3", "version": ""},
            }
        },
    )
    assert err
    assert "Applied" not in out
    assert "Skipped" not in out


def test_import_two_settings_show_skipped():
    out, err = std_import(
        {
            "settings": {
                "TITLE": {"value": "The New Book Store", "version": "2"},
                "BOOKS_ON_HOME_PAGE": {"value": "3", "version": ""},
            }
        },
        "--show-skipped",
    )
    assert err
    assert "Applied" not in out
    assert "Skipped" in out


def test_import_two_setting_one_confirmed():
    out, err = std_import(
        {
            "settings": {
                "TITLE": {"value": "The New Book Store", "version": ""},
                "BOOKS_ON_HOME_PAGE": {"value": "4", "version": ""},
            }
        },
        "--import",
        "--names",
        "TITLE",
    )
    assert not err
    assert "Applied" in out
    assert ContentSetting.objects.get(name="TITLE").value == "The New Book Store"
    assert ContentSetting.objects.get(name="BOOKS_ON_HOME_PAGE").value == "3"
