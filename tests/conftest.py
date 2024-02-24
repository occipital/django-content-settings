import django
import pytest

from django.contrib.auth import get_user_model


def pytest_configure(config):
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
        },
        SITE_ID=1,
        USE_TZ=True,
        SECRET_KEY="not very secret in tests",
        USE_I18N=True,
        LANGUAGES=[
            ("en", "English"),
            ("es", "Spanish"),
        ],
        STATIC_URL="/static/",
        ROOT_URLCONF="tests.urls",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {
                    "debug": True,  # We want template errors to raise
                    "context_processors": [
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                        "django.template.context_processors.request",
                        "content_settings.context_processors.content_settings",
                    ],
                },
            },
        ],
        MIDDLEWARE=(
            "django.middleware.common.CommonMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.locale.LocaleMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "content_settings.middlewares.preivew_on_site",
            "django.contrib.messages.middleware.MessageMiddleware",
        ),
        INSTALLED_APPS=(
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django.contrib.staticfiles",
            "django.contrib.messages",
            "content_settings",
            "tests.books",
        ),
        PASSWORD_HASHERS=("django.contrib.auth.hashers.MD5PasswordHasher",),
        CONTENT_SETTINGS_USER_DEFINED_TYPES=[
            (
                "line",
                "tests.books.content_settings.PublicSimpleString",
                "Line (Public)",
            ),
            ("text", "content_settings.types.basic.SimpleText", "Text"),
            ("html", "content_settings.types.basic.SimpleHTML", "HTML"),
        ],
    )

    django.setup()


@pytest.fixture(autouse=True)
def reset_all_values():
    from content_settings.caching import reset_all_values

    reset_all_values()


@pytest.fixture
def testadmin():
    return get_user_model().objects.get_or_create(
        username="testadmin", is_staff=True, is_superuser=True
    )[0]


@pytest.fixture
def webtest_admin(django_app_factory, testadmin):
    web = django_app_factory(csrf_checks=False)
    web.set_user(testadmin)
    return web


@pytest.fixture
def testuser():
    return get_user_model().objects.get_or_create(username="testuser")[0]


@pytest.fixture
def webtest_user(django_app_factory, testuser):
    web = django_app_factory(csrf_checks=False)
    web.set_user(testuser)
    return web


@pytest.fixture
def webtest_staff(django_app_factory):
    from django.contrib.auth.models import Permission

    user, _ = get_user_model().objects.get_or_create(
        username="teststaff", is_staff=True
    )
    for codename in ("change_contentsetting", "view_contentsetting"):
        perm = Permission.objects.get(codename=codename)
        user.user_permissions.add(perm)

    web = django_app_factory(csrf_checks=False)
    web.set_user(user)
    return web
