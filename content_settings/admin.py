import urllib.parse
from collections import defaultdict

from django.contrib import admin
from django.forms import ModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin.views.main import ChangeList
from django.urls import path
from django.http import JsonResponse
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.utils.text import capfirst
from django.template.response import TemplateResponse
from django.contrib.messages import add_message, ERROR
from django.utils.translation import gettext as _


from .models import ContentSetting, HistoryContentSetting, UserTagSetting
from .context_managers import content_settings_context
from .conf import ALL
from .settings import USER_TAGS


def user_able_to_update(user, name):
    return ALL[name].update_permission is None or ALL[name].update_permission(user)


TAGS_PARAM = "tags"
TAGS_SPLITER = "|"


def get_selected_tags_from_params(params):
    if TAGS_PARAM not in params:
        return set()
    return set(params[TAGS_PARAM].split(TAGS_SPLITER))


class SettingsChangeList(ChangeList):
    def get_filters_params(self, *args, **kwargs):
        params = super().get_filters_params(*args, **kwargs)
        if TAGS_PARAM in params:
            del params[TAGS_PARAM]
        return params

    def get_queryset(self, request, *args, **kwargs):
        q = super().get_queryset(request, *args, **kwargs)

        tags = get_selected_tags_from_params(self.params)
        if not tags:
            return q

        all_keys = []
        user_settings = UserTagSetting.get_user_settings(request.user)
        for name, val in ALL.items():
            val_tags = val.get_tags() | user_settings[name]
            if not val_tags or tags - val_tags:
                continue

            all_keys.append(name)

        return q.filter(name__in=all_keys)


class ContentSettinForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ContentSettinForm, self).__init__(*args, **kwargs)
        self.fields["value"].strip = False

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        model = ContentSetting
        fields = ["value"]


class ContentSettingAdmin(admin.ModelAdmin):
    list_display = ["name", "value", "help", "tags", "marks"]
    list_editable = [
        "value",
    ]
    search_fields = ["name", "value"]
    readonly_fields = [
        "py_data",
        "name",
        "help",
        "version",
        "default_value",
        "fetch_one_setting",
    ]
    history_list_display = ["value"]
    form = ContentSettinForm

    def save_model(self, request, obj, form, change):
        if user_able_to_update(request.user, obj.name):
            super().save_model(request, obj, form, change)
            HistoryContentSetting.update_last_record_for_name(obj.name, request.user)
        else:
            add_message(
                request,
                ERROR,
                _("You are not allowed to change %(name)s") % {"name": obj.name},
            )

    def get_search_results(self, request, queryset, search_term):
        qs, search_use_distinct = super().get_search_results(
            request, queryset, search_term
        )

        if search_term:
            help_names = [
                name
                for name, value in ALL.items()
                if search_term.lower() in value.help.lower()
            ]
            help_names = set(help_names).difference(
                set(qs.values_list("name", flat=True))
            )
            if help_names:
                qs = qs.union(ContentSetting.objects.filter(name__in=help_names))

        return qs, search_use_distinct

    def get_changelist(self, request, **kwargs):
        return SettingsChangeList

    def context_tags(self, request):
        extra_context = {}
        selected_tags = get_selected_tags_from_params(request.GET)

        def q_tags(tags):
            if not tags:
                return "?"
            return "?" + TAGS_PARAM + "=" + urllib.parse.quote(TAGS_SPLITER.join(tags))

        def q_add_tag(tag):
            return q_tags(selected_tags | set([tag]))

        def q_remove_tag(tag):
            return q_tags(selected_tags - set([tag]))

        extra_context["selected_tags"] = [
            {
                "tag": USER_TAGS[tag][0] if tag in USER_TAGS else tag,
                "url": q_remove_tag(tag),
            }
            for tag in sorted(selected_tags)
        ]

        tags_stat = defaultdict(int)
        user_settings = UserTagSetting.get_user_settings(request.user)
        for name, val in ALL.items():
            val_tags = val.get_tags() | user_settings[name]
            if selected_tags and (not val_tags or selected_tags - val_tags):
                continue

            for tag in val_tags - selected_tags:
                tags_stat[tag] += 1

        extra_context["available_tags"] = [
            {
                "tag": USER_TAGS[tag][0] if tag in USER_TAGS else tag,
                "url": q_add_tag(tag),
                "total": total,
            }
            for tag, total in sorted(
                tags_stat.items(), key=lambda a: a[0] and a[0] not in USER_TAGS
            )
        ]

        return extra_context

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(
            request, {**(extra_context or {}), **self.context_tags(request)}
        )

    def context_tags_view(self, request):
        return TemplateResponse(
            request,
            "admin/content_settings/contentsetting/context_tags.html",
            self.context_tags(request),
        )

    def history_view(self, request, object_id, extra_context=None):

        # First check if the user can see this history.
        model = self.model
        obj = self.get_object(request, unquote(object_id))
        if obj is None:
            return self._get_obj_does_not_exist_redirect(
                request, model._meta, object_id
            )

        if not self.has_view_or_change_permission(request, obj):
            raise PermissionDenied

        opts = model._meta
        app_label = opts.app_label

        context = {
            **self.admin_site.each_context(request),
            "title": f"Change history: {obj}",
            "subtitle": None,
            "module_name": str(capfirst(opts.verbose_name_plural)),
            "object": obj,
            "opts": opts,
            "preserved_filters": self.get_preserved_filters(request),
            "action_list": HistoryContentSetting.gen_unique_records(obj.name),
            **(extra_context or {}),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request, f"admin/{app_label}/{opts.model_name}/object_history.html", context
        )

    def get_changelist_form(self, request, **kwargs):
        return ContentSettinForm

    def has_delete_permission(self, *args):
        return False

    def has_add_permission(self, *args):
        return False

    def help(self, obj):
        try:
            help = ALL[obj.name].get_help()
        except KeyError:
            return "(the setting is not using)"
        if obj.value.replace("\r", "") != ALL[obj.name].default:
            help = "<i>(value is not default)</i> <br>" + help
        return mark_safe(help)

    def tags(self, obj):
        try:
            tags = ALL[obj.name].get_tags()
        except KeyError:
            return "(the setting is not using)"
        else:
            if not tags:
                return "---"
            return ", ".join(tags)

    def marks(self, obj):
        return mark_safe(
            "".join(
                f"""<span>
            <span class="user_tag user_tag_selected user_tag_hidden" data-tag="{tag}" data-name="{obj.name}">{marks[0]}</span>
            <span class="user_tag user_tag_hidden" data-tag="{tag}" data-name="{obj.name}">{marks[1]}</span>
            </span>"""
                for tag, marks in USER_TAGS.items()
            )
        )

    def py_data(self, obj):
        try:
            return mark_safe(ALL[obj.name].get_admin_preview_value(obj.value, obj.name))
        except KeyError:
            return ""

    def default_value(self, obj):
        from django.utils.html import escape

        attr_default = (
            ALL[obj.name]
            .default.replace("&", "&amp;")
            .replace("\n", "&NewLine;")
            .replace('"', "&quot;")
        )
        try:
            return mark_safe(
                f"""
            <pre class="default_value">{escape(ALL[obj.name].default)}</pre>
            <a class="reset_default" data-value="{attr_default}" style="cursor: pointer; color:var(--link-fg)">Reset ("save" is required for applying)</a>
            """
            )
        except KeyError:
            return ""

    def fetch_one_setting(self, obj):
        if not obj.name:
            return ""

        def get_fetch_reverse(name):
            return reverse(
                "content_settings:fetch_one_setting",
                kwargs={"name": name.lower().replace("_", "-")},
            )

        urls = [get_fetch_reverse(obj.name)]
        fetch_groups = ALL[obj.name].fetch_groups
        if fetch_groups is not None:
            if isinstance(fetch_groups, str):
                fetch_groups = [fetch_groups]

            urls += [get_fetch_reverse(n) for n in fetch_groups]

        return "\n".join(urls)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "preview/",
                self.admin_site.admin_view(self.preview_setting),
                name="preview_setting",
            ),
            path("add-tag/", self.admin_site.admin_view(self.add_tag), name="add_tag"),
            path(
                "remove-tag/",
                self.admin_site.admin_view(self.remove_tag),
                name="remove_tag",
            ),
            path(
                "context-tags/",
                self.admin_site.admin_view(self.context_tags_view),
                name="context_tags",
            ),
        ]
        return custom_urls + urls

    # ajax view that creates UserTagSetting
    def add_tag(self, request):
        try:
            name = request.POST["name"]
            tag = request.POST["tag"]
            UserTagSetting.objects.create(
                user=request.user,
                name=name,
                tag=tag,
            )
        except Exception as e:
            return JsonResponse(
                {
                    "error": str(e),
                }
            )
        else:
            return JsonResponse(
                {
                    "success": True,
                }
            )

    # ajax view that removes UserTagSetting
    def remove_tag(self, request):
        try:
            name = request.POST["name"]
            tag = request.POST["tag"]
            UserTagSetting.objects.get(
                user=request.user,
                name=name,
                tag=tag,
            ).delete()
        except Exception as e:
            return JsonResponse(
                {
                    "error": str(e),
                }
            )
        else:
            return JsonResponse(
                {
                    "success": True,
                }
            )

    def preview_setting(self, request):
        setting = ALL[request.POST["name"]]
        value = request.POST["value"]

        other_values = {
            name[2:]: value
            for name, value in request.POST.items()
            if name.startswith("o_")
        }
        try:
            setting.validate_value(value)
        except Exception as e:
            return JsonResponse(
                {
                    "error": str(e),
                }
            )
        with content_settings_context(**other_values):
            return JsonResponse(
                {
                    "html": setting.get_admin_preview_value(
                        value, request.POST["name"]
                    ),
                }
            )


admin.site.register(ContentSetting, ContentSettingAdmin)
