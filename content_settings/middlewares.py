from .context_managers import content_settings_context
from .models import UserPreview


def preivew_on_site(get_response):
    def middleware(request):
        if not request.user.has_perm("content_settings.can_preview_on_site"):
            return get_response(request)

        preview_settings = dict(
            UserPreview.objects.filter(user=request.user).values_list("name", "value")
        )
        if not preview_settings:
            return get_response(request)

        with content_settings_context(**preview_settings):
            return get_response(request)

    return middleware
