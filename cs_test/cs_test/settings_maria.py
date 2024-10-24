from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "django_db",
        "USER": "django_user",
        "PASSWORD": "djangopassword",
        "HOST": "db",
        "PORT": "3306",
    }
}
