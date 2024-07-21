"""
Available middlewares for the content settings.
"""

from .context_managers import content_settings_context
from .models import UserPreview
from .settings import PREVIEW_ON_SITE_SHOW


def preivew_on_site(get_response):
    """
    the middleware required for previewing the content settings on the site.

    It checks content_settings.can_preview_on_site permission for the user and if the user has it, then the middleware will preview the content settings for the user.
    """

    def middleware(request):
        if not PREVIEW_ON_SITE_SHOW or not request.user.has_perm(
            "content_settings.can_preview_on_site"
        ):
            return get_response(request)

        preview_settings = dict(
            UserPreview.objects.filter(user=request.user).values_list("name", "value")
        )
        if not preview_settings:
            return get_response(request)

        with content_settings_context(**preview_settings, _raise_errors=False):
            return get_response(request)

    return middleware
