import pytest

from django.test import Client
from django.contrib.auth import get_user_model

from content_settings.models import ContentSetting
from content_settings.context_managers import content_settings_context

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_simple():
    pass
