from django.apps import AppConfig


class StaticContentConfig(AppConfig):
    name = "content_settings"
    verbose_name = "Content Settings"

    def ready(self):
        import content_settings.signals
        from content_settings.caching import reset_all_values

        reset_all_values()
