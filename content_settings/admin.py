import urllib.parse
from collections import defaultdict
import inspect

from django.contrib import admin
from django.forms import ModelForm
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin.views.main import ChangeList
from django.urls import path
from django.http import JsonResponse
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.urls.exceptions import NoReverseMatch
from django.utils.text import capfirst
from django.template.response import TemplateResponse
from django.contrib.messages import add_message, ERROR
from django.utils.translation import gettext as _
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import resolve_url
from django.shortcuts import get_object_or_404

from .models import (
    ContentSetting,
    HistoryContentSetting,
    UserTagSetting,
    UserPreview,
    UserPreviewHistory,
)
from .context_managers import content_settings_context
from .conf import USER_DEFINED_TYPES_INSTANCE
from .settings import USER_TAGS, USER_DEFINED_TYPES, PREVIEW_ON_SITE_HREF
from .caching import get_type_by_name


def user_able_to_update(user, name, user_defined_type=None):
    cs_type = get_type_by_name(name)
    if cs_type is None and user_defined_type is not None:
        cs_type = USER_DEFINED_TYPES_INSTANCE[user_defined_type]()
    if cs_type is None:
        return False
    return cs_type.can_update(user)


TAGS_PARAM = "tags"
TAGS_SPLITER = "|"


def get_selected_tags_from_params(params):
    if TAGS_PARAM not in params:
        return set()
    return set(params[TAGS_PARAM].split(TAGS_SPLITER))


def html_classes(name):
    classes = "</li><li>".join(
        f"{cls.__name__} <i>from {cls.__module__}</i>"
        for cls in inspect.getmro(get_type_by_name(name).__class__)
        if cls.__name__
        and cls.__module__ != "builtins"
        and (cls.__module__, cls.__name__)
        not in (
            ("content_settings.types.basic", "BaseSetting"),
            ("content_settings.types.basic", "SimpleString"),
        )
    )
    if not classes:
        return ""

    return mark_safe(
        f"<div><a class='replace_with_ul'>...</a> <ul style='display: none; margin-top: 1.5em'><li>{classes}</li></ul></div>"
    )


class SettingsChangeList(ChangeList):
    def get_filters_params(self, *args, **kwargs):
        params = super().get_filters_params(*args, **kwargs)
        if TAGS_PARAM in params:
            del params[TAGS_PARAM]
        return params

    def get_queryset(self, request, *args, **kwargs):
        from .conf import get_type_by_name

        q = super().get_queryset(request, *args, **kwargs)
        user = request.user

        tags = get_selected_tags_from_params(self.params)
        if tags:

            user_settings = list(
                UserTagSetting.objects.filter(
                    user=request.user, tag__in=tags
                ).values_list("name", flat=True)
            )
            if user_settings:
                q = q.filter(name__in=user_settings)

            combine = Q()
            for tag in tags:
                if tag in USER_TAGS:
                    continue
                combine &= Q(tags__iregex=rf"(^|\n){tag}($|\n)")

            q = q.filter(combine)
        # This is terrable
        # But I don't know how to do it better
        # I need to filter out the names user don't have permissions to see

        names = list(q.values_list("name", flat=True))
        return q.filter(
            ~Q(
                name__in=[
                    name
                    for name in names
                    if not get_type_by_name(name)
                    or get_type_by_name(name).constant
                    or not get_type_by_name(name).can_view(user)
                ]
            )
        )


class ContentSettinForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ContentSettinForm, self).__init__(*args, **kwargs)
        if self.instance.name:
            cs_type = get_type_by_name(self.instance.name)
            if cs_type:
                self.fields["value"] = cs_type.field
        self.fields["value"].strip = False

        if "user_defined_type" in self.fields:
            self.fields["user_defined_type"].widget = forms.Select(
                choices=[(v[0], v[2]) for v in USER_DEFINED_TYPES]
            )

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        model = ContentSetting
        fields = ["value"]


class ContentSettingAdmin(admin.ModelAdmin):
    list_display = ["name", "value", "setting_help", "setting_tags", "marks"]
    list_editable = [
        "value",
    ]
    search_fields = ["name", "value", "tags", "help"]
    readonly_fields = [
        "py_data",
        "name",
        "setting_help",
        "setting_tags",
        "version",
        "default_value",
        "fetch_one_setting",
    ]
    history_list_display = ["value"]
    form = ContentSettinForm

    def save_model(self, request, obj, form, change):
        if user_able_to_update(request.user, obj.name, obj.user_defined_type):
            prev_obj = ContentSetting.objects.filter(pk=obj.pk).first()
            if prev_obj and not any(
                getattr(prev_obj, name) != getattr(obj, name)
                for name in ("value", "tags", "help", "user_defined_type", "name")
            ):
                return

            if "_preview_on_site" in request.POST:
                try:
                    preview_setting = UserPreview.objects.get(
                        user=request.user, name=obj.name
                    )
                except UserPreview.DoesNotExist:
                    preview_setting = UserPreview.objects.create(
                        user=request.user,
                        name=obj.name,
                        value=obj.value,
                        from_value=prev_obj.value,
                    )
                else:
                    preview_setting.value = obj.value
                    preview_setting.save()
                UserPreviewHistory.user_record(
                    request.user, preview_setting, UserPreviewHistory.STATUS_CREATED
                )
            else:
                super().save_model(request, obj, form, change)
                HistoryContentSetting.update_last_record_for_name(
                    obj.name, request.user
                )
        else:
            add_message(
                request,
                ERROR,
                _("You are not allowed to change %(name)s") % {"name": obj.name},
            )

    def get_readonly_fields(self, request, obj=None):
        if not USER_DEFINED_TYPES or obj and not obj.user_defined_type:
            return super().get_readonly_fields(request, obj)

        return [
            v
            for v in super().get_readonly_fields(request, obj)
            if v
            not in (
                "name",
                "setting_help",
                "setting_tags",
            )
        ]

    def get_form(self, request, obj=None, change=False, **kwargs):
        if USER_DEFINED_TYPES and not obj or obj.user_defined_type:
            kwargs["fields"] = ["user_defined_type", "name", "value", "help", "tags"]
        else:
            kwargs["fields"] = [
                "value",
            ]

        return super().get_form(request, obj=None, change=False, **kwargs)

    def get_changelist(self, request, **kwargs):
        return SettingsChangeList

    def context_preview_settings(self, request):
        return {
            "preview_settings": UserPreview.objects.filter(user=request.user),
            "PREVIEW_ON_SITE_HREF": PREVIEW_ON_SITE_HREF,
        }

    def context_tags(self, request):
        from .conf import get_type_by_name

        extra_context = {}
        selected_tags = get_selected_tags_from_params(request.GET)

        if "q" in request.GET:
            init_q = "?q=" + urllib.parse.quote(request.GET["q"]) + "&"
        else:
            init_q = "?"

        def q_tags(tags):
            if not tags:
                return init_q
            return (
                init_q + TAGS_PARAM + "=" + urllib.parse.quote(TAGS_SPLITER.join(tags))
            )

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

        for cs in self.get_changelist_instance(request).get_queryset(request):
            cs_type = get_type_by_name(cs.name)
            if not cs_type or not cs_type.can_view(request.user) or cs_type.constant:
                continue
            val_tags = cs.tags_set | user_settings[cs.name]
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
        def key_value_from_request():
            total_forms = int(request.POST["form-TOTAL_FORMS"])

            for i in range(total_forms):
                yield ContentSetting.objects.get(
                    id=request.POST[f"form-{i}-id"]
                ).name, request.POST[f"form-{i}-value"]

        super_changelist = super().changelist_view

        def gen_response():
            return super_changelist(
                request,
                {
                    **(extra_context or {}),
                    **self.context_tags(request),
                    **self.context_preview_settings(request),
                },
            )

        if not request.method == "POST" or "_save" not in request.POST:
            return gen_response()

        with content_settings_context(
            _raise_errors=False,
            **{name: value for name, value in key_value_from_request()},
        ):
            return gen_response()

    def context_tags_view(self, request):
        return TemplateResponse(
            request,
            "admin/content_settings/contentsetting/context_tags.html",
            self.context_tags(request),
        )

    def change_view(self, request, object_id, *args, **kwargs):
        from .conf import get_type_by_name

        cs = ContentSetting.objects.filter(pk=object_id).first()

        cs_type = get_type_by_name(cs.name)
        if cs and not cs_type or not cs_type.can_view(request.user) or cs_type.constant:
            raise PermissionDenied

        return super().change_view(request, object_id, *args, **kwargs)

    def history_view(self, request, object_id, extra_context=None):
        from .conf import get_type_by_name

        # First check if the user can see this history.
        model = self.model
        obj = self.get_object(request, unquote(object_id))
        if obj is None:
            return self._get_obj_does_not_exist_redirect(
                request, model._meta, object_id
            )

        cs_type = get_type_by_name(obj.name)
        if (
            not self.has_view_or_change_permission(request, obj)
            or not cs_type
            or not cs_type.can_view_history(request.user)
            or cs_type.constant
        ):
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

    def has_delete_permission(self, request, obj=None):
        default_del_permission = super().has_delete_permission(request, obj)
        if not default_del_permission or not USER_DEFINED_TYPES:
            return False
        return not obj or obj.user_defined_type is not None

    def has_add_permission(self, *args):
        return super().has_add_permission(*args) and USER_DEFINED_TYPES

    def has_change_permission(self, request, obj=None):
        default_change_permission = super().has_change_permission(request, obj)
        if not default_change_permission:
            return False
        if not obj:
            return True
        return user_able_to_update(request.user, obj.name)

    def setting_help(self, obj):
        cs_type = get_type_by_name(obj.name)
        if cs_type is None or cs_type.constant:
            return "(the setting is not using)"

        if obj.user_defined_type:
            help = cs_type.get_help()
        else:
            help = obj.help
        return mark_safe(help + html_classes(obj.name))

    setting_help.short_description = "Help"

    def setting_tags(self, obj):
        cs_type = get_type_by_name(obj.name)
        if cs_type is None or cs_type.constant:
            return "(the setting is not using)"

        tags = obj.tags_set

        if not tags:
            return "---"
        return ", ".join(tags)

    setting_tags.short_description = "Tags"

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
        cs_type = get_type_by_name(obj.name)

        if cs_type is None or cs_type.constant:
            return ""

        full_value = cs_type.get_full_admin_preview_value(obj.value, obj.name)
        if "error" in full_value:
            return mark_safe(f"<pre style='color: red'>{full_value['error']}</pre>")
        if "html" in full_value:
            return mark_safe(full_value["html"])

    def default_value(self, obj):
        from django.utils.html import escape

        cs_type = get_type_by_name(obj.name)

        if cs_type is None or cs_type.constant:
            return ""

        attr_default = (
            cs_type.default.replace("&", "&amp;")
            .replace("\n", "&NewLine;")
            .replace('"', "&quot;")
        )
        return mark_safe(
            f"""
        <pre class="default_value">{escape(cs_type.default)}</pre>
        <a class="reset_default" data-value="{attr_default}" style="cursor: pointer; color:var(--link-fg)">Reset ("save" is required for applying)</a>
        """
        )

    def fetch_one_setting(self, obj):
        if not obj.name:
            return ""

        try:
            return reverse(
                "content_settings:fetch_one_setting",
                kwargs={"name": obj.name.lower().replace("_", "-")},
            )
        except NoReverseMatch:
            return ""

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
            path(
                "apply-preview-on-site/",
                self.admin_site.admin_view(self.apply_preview_on_site),
                name="apply_preview_on_site",
            ),
            path(
                "reset-preview-on-site/",
                self.admin_site.admin_view(self.reset_preview_on_site),
                name="reset_preview_on_site",
            ),
            path(
                "remove-preview-on-site/",
                self.admin_site.admin_view(self.remove_preview_on_site),
                name="remove_preview_on_site",
            ),
        ]
        return custom_urls + urls

    def remove_preview_on_site(self, request):
        preview_setting = get_object_or_404(
            UserPreview, user=request.user, name=request.GET["name"]
        )
        UserPreviewHistory.user_record(
            request.user, preview_setting, UserPreviewHistory.STATUS_REMOVED
        )
        preview_setting.delete()
        self.message_user(request, "Preview setting removed", messages.SUCCESS)
        return HttpResponseRedirect(
            request.META.get("HTTP_REFERER", resolve_url("admin:index"))
        )

    def apply_preview_on_site(self, request):
        for preview_setting in UserPreview.objects.filter(user=request.user):
            try:
                setting = ContentSetting.objects.get(name=preview_setting.name)
            except ContentSetting.DoesNotExist:
                UserPreviewHistory.user_record(
                    request.user, preview_setting, UserPreviewHistory.STATUS_IGNORED
                )
            else:
                cs_type = get_type_by_name(preview_setting.name)
                assert cs_type.can_update(request.user)
                cs_type.validate_value(preview_setting.value)

                UserPreviewHistory.user_record(
                    request.user, preview_setting, UserPreviewHistory.STATUS_APPLIED
                )
                setting.value = preview_setting.value
                setting.save()
                HistoryContentSetting.update_last_record_for_name(
                    setting.name, request.user
                )

            preview_setting.delete()

        self.message_user(request, "Preview settings applied", messages.SUCCESS)
        return HttpResponseRedirect(
            request.META.get("HTTP_REFERER", resolve_url("admin:index"))
        )

    def reset_preview_on_site(self, request):
        for preview_setting in UserPreview.objects.filter(user=request.user):
            UserPreviewHistory.user_record(
                request.user, preview_setting, UserPreviewHistory.STATUS_REMOVED
            )
            preview_setting.delete()

        self.message_user(request, "Preview settings removed", messages.SUCCESS)
        return HttpResponseRedirect(
            request.META.get("HTTP_REFERER", resolve_url("admin:index"))
        )

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
        if request.POST.get("user_defined_type"):
            try:
                cs_type_instance = USER_DEFINED_TYPES_INSTANCE[
                    request.POST["user_defined_type"]
                ]
            except KeyError:
                return JsonResponse(
                    {
                        "error": "Invalid user_defined_type",
                        "html": "",
                    }
                )
            else:
                cs_type = cs_type_instance()
        else:
            cs_type = get_type_by_name(request.POST["name"])
        if cs_type is None or cs_type.constant:
            return JsonResponse({"html": "", "error": "Invalid name"})

        value = request.POST["value"]

        other_values = {
            name[2:]: value
            for name, value in request.POST.items()
            if name.startswith("o_")
        }

        params = {
            name[2:]: value
            for name, value in request.POST.items()
            if name.startswith("p_")
        }

        with content_settings_context(**other_values):
            return JsonResponse(
                cs_type.get_full_admin_preview_value(
                    value, request.POST["name"], user=request.user, **params
                )
            )


class HistoryContentSettingAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "value",
        "user_defined_type",
        "version",
        "tags",
        "help",
        "was_changed",
        "user",
    ]
    list_filter = [
        "was_changed",
        "name",
    ]
    search_fields = ["name", "value", "tags", "help"]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, *args):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(ContentSetting, ContentSettingAdmin)
admin.site.register(HistoryContentSetting, HistoryContentSettingAdmin)
