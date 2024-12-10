from typing import Any
import urllib.parse
from collections import defaultdict
import json

from django.contrib import admin
from django.forms import ModelForm
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin.views.main import ChangeList
from django.urls import path
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.utils.text import capfirst
from django.template.response import TemplateResponse
from django.contrib.messages import add_message, ERROR
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import resolve_url
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.core.exceptions import ValidationError

from .models import (
    ContentSetting,
    HistoryContentSetting,
    UserTagSetting,
    UserPreview,
    UserPreviewHistory,
)
from .context_managers import content_settings_context
from .conf import (
    USER_DEFINED_TYPES_INSTANCE,
    USER_DEFINED_TYPES_INITIAL,
    content_settings,
    validate_all_with_context,
)
from .settings import (
    USER_TAGS,
    USER_DEFINED_TYPES,
    PREVIEW_ON_SITE_HREF,
    ADMIN_CHECKSUM_CHECK_BEFORE_SAVE,
    UI_DOC_URL,
    PREVIEW_ON_SITE_SHOW,
)
from .caching import get_type_by_name
from .utils import class_names
from .export import export_to_format, preview_data, import_to


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
        f"{cls_name} <i>from {module_name}</i>"
        for cls_name, module_name in class_names(get_type_by_name(name).__class__)
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


class ContentSettingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ContentSettingForm, self).__init__(*args, **kwargs)
        if self.instance.name:
            cs_type = get_type_by_name(self.instance.name)
            if cs_type:
                self.fields["value"] = cs_type.get_field()
        self.fields["value"].strip = False

        if "user_defined_type" in self.fields:
            self.fields["user_defined_type"].widget = forms.Select(
                choices=[(v[0], v[2]) for v in USER_DEFINED_TYPES]
            )

    class Meta:
        model = ContentSetting
        fields = ["value"]


# we want to have a separate form for a single edit interface
# because we want to validate the chain of content setting changes
class ContentSettingFormWithChainValidation(ContentSettingForm):
    def clean(self):
        ret = super().clean()
        if self.instance and not self.errors:
            validate_all_with_context(
                {
                    (self.cleaned_data.get("name") or self.instance.name): (
                        (
                            self.cleaned_data["value"],
                            self.cleaned_data.get("user_defined_type"),
                            self.cleaned_data.get("tags"),
                            self.cleaned_data.get("help"),
                        )
                        if "user_defined_type" in self.cleaned_data
                        else self.cleaned_data["value"]
                    )
                }
            )
        return ret


class ContentSettingAdmin(admin.ModelAdmin):
    list_display = ["name", "value", "setting_help_and_tags", "marks"]
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
    ]
    history_list_display = ["value"]
    form = ContentSettingFormWithChainValidation
    actions = ["export_as_json", "view_as_json"]

    def export_as_json(self, request, queryset, download=True):
        json_data = export_to_format(
            row for row in queryset if get_type_by_name(row.name).can_view(request.user)
        )
        response = HttpResponse(content_type="application/json")
        if download:
            response["Content-Disposition"] = (
                'attachment; filename="content_settings.json"'
            )
        response.write(json_data)
        return response

    export_as_json.short_description = _("Export selected content settings")

    def view_as_json(self, request, queryset):
        return self.export_as_json(request, queryset, download=False)

    view_as_json.short_description = _("View selected content settings as JSON")

    def save_model(self, request, obj, form, change):
        if user_able_to_update(request.user, obj.name, obj.user_defined_type):
            prev_obj = ContentSetting.objects.filter(pk=obj.pk).first()
            if prev_obj and not any(
                getattr(prev_obj, name) != getattr(obj, name)
                for name in ("value", "tags", "help", "user_defined_type", "name")
            ):
                return

            if "_preview_on_site" in request.POST:
                if obj.user_defined_type:
                    UserPreview.add_by_user(
                        user=request.user,
                        name=obj.name,
                        value=obj.value,
                        user_defined_type=obj.user_defined_type,
                        tags=obj.tags_set,
                        help=obj.help,
                    )
                else:
                    UserPreview.add_by_user(
                        user=request.user,
                        name=obj.name,
                        value=obj.value,
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
        if not PREVIEW_ON_SITE_SHOW or not request.user.has_perm(
            "content_settings.can_preview_on_site"
        ):
            return {}

        return {
            "preview_settings": UserPreview.objects.filter(user=request.user),
            "PREVIEW_ON_SITE_HREF": PREVIEW_ON_SITE_HREF,
            "PREVIEW_ON_SITE_SHOW": True,
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

    def form_checksum_valid(self, request):
        if (
            ADMIN_CHECKSUM_CHECK_BEFORE_SAVE
            and request.POST["content_settings_form_checksum"]
            != content_settings.form_checksum
        ):
            add_message(
                request,
                ERROR,
                _(
                    "The content settings have been changed by another user. Please reload the page and try again. (or disable ADMIN_CHECKSUM_CHECK_BEFORE_SAVE in settings)"
                ),
            )
            return False
        return True

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if request.method == "POST" and not self.form_checksum_valid(request):
            return HttpResponseRedirect(request.path)
        return super().changeform_view(
            request,
            object_id=object_id,
            form_url=form_url,
            extra_context={
                **(extra_context or {}),
                **self.context_preview_settings(request),
            },
        )

    def get_changelist_formset(self, request, **kwargs):
        # validation of changing this particular value didn't change other values in the chain
        # this is done by using validate_all_with_context
        BaseFormset = super().get_changelist_formset(request, **kwargs)

        class ContentSettingFormset(BaseFormset):
            def clean(self):
                ret = super().clean()
                if hasattr(self, "cleaned_data"):
                    validate_all_with_context(
                        {data["id"].name: data["value"] for data in self.cleaned_data}
                    )
                return ret

        return ContentSettingFormset

    def changelist_view(self, request, extra_context=None):
        if request.method == "POST" and not self.form_checksum_valid(request):
            return HttpResponseRedirect(request.path)

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
                    "UI_DOC_URL": UI_DOC_URL,
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

    def change_view(self, request, object_id, form_url="", extra_context=None):
        from .conf import get_type_by_name

        cs = ContentSetting.objects.filter(pk=object_id).first()

        cs_type = get_type_by_name(cs.name)
        if cs and not cs_type or not cs_type.can_view(request.user) or cs_type.constant:
            raise PermissionDenied

        extra_context = {
            "PREVIEW_ON_SITE_SHOW": PREVIEW_ON_SITE_SHOW
            and request.user.has_perm("content_settings.can_preview_on_site"),
            **(extra_context or {}),
        }

        return super().change_view(request, object_id, form_url, extra_context)

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
        return ContentSettingForm

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
            return _("(the setting is not using)")

        if obj.user_defined_type:
            help = cs_type.get_help()
        else:
            help = obj.help
        return mark_safe(help + html_classes(obj.name))

    setting_help.short_description = _("Help")

    def setting_help_and_tags(self, obj):
        return mark_safe(
            f"<div style='min-width: 300px;'>{self.setting_help(obj)}<br>{self.setting_tags(obj)}</div>"
        )

    setting_help_and_tags.short_description = _("Help")

    def setting_tags(self, obj):
        cs_type = get_type_by_name(obj.name)
        if cs_type is None or cs_type.constant:
            return _("(the setting is not using)")

        tags = obj.tags_set

        if not tags:
            return "---"
        return ", ".join(tags)

    setting_tags.short_description = _("Tags")

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
        cs_type = get_type_by_name(obj.name)

        if cs_type is None or cs_type.constant:
            return ""

        attr_default = (
            cs_type.default.replace("&", "&amp;")
            .replace("\n", "&NewLine;")
            .replace('"', "&quot;")
        )

        label = _('Reset ("save" is required for applying)')
        return mark_safe(
            f"""
        <pre class="default_value">{escape(cs_type.default)}</pre>
        <a class="reset_default" data-value="{attr_default}" style="cursor: pointer; color:var(--link-fg)">{label}</a>
        """
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "preview/",
                self.admin_site.admin_view(self.preview_setting),
                name="content_settings_preview_setting",
            ),
            path(
                "add-tag/",
                self.admin_site.admin_view(self.add_tag),
                name="content_settings_add_tag",
            ),
            path(
                "remove-tag/",
                self.admin_site.admin_view(self.remove_tag),
                name="content_settings_remove_tag",
            ),
            path(
                "context-tags/",
                self.admin_site.admin_view(self.context_tags_view),
                name="content_settings_context_tags",
            ),
            path(
                "apply-preview-on-site/",
                self.admin_site.admin_view(self.apply_preview_on_site),
                name="content_settings_apply_preview_on_site",
            ),
            path(
                "reset-preview-on-site/",
                self.admin_site.admin_view(self.reset_preview_on_site),
                name="content_settings_reset_preview_on_site",
            ),
            path(
                "remove-preview-on-site/",
                self.admin_site.admin_view(self.remove_preview_on_site),
                name="content_settings_remove_preview_on_site",
            ),
            path(
                "import-json/",
                self.admin_site.admin_view(self.import_json_view),
                name="content_settings_import_json",
            ),
        ]
        return custom_urls + urls

    def remove_preview_on_site(self, request):
        preview_setting = get_object_or_404(
            UserPreview, user=request.user, name=request.GET["name"]
        )
        UserPreviewHistory.user_record(
            preview_setting, UserPreviewHistory.STATUS_REMOVED
        )
        preview_setting.delete()
        self.message_user(request, _("Preview setting removed"), messages.SUCCESS)
        return HttpResponseRedirect(
            request.META.get("HTTP_REFERER", resolve_url("admin:index"))
        )

    def apply_preview_on_site(self, request):
        """
        The view that applies collected preview settings to the actual settings.

        Consist of the following stages:

        * validate each value independently
        * previous value was updated before applying
        * validate the whole chain of values
        * apply the values

        Edge cases:

        * preview settings will be automatically removed in case the value is not longer passible to apply
        * if setting was changed and now it is equal to preview setting - the preview will be removed
        """

        def redirect_back():
            return HttpResponseRedirect(
                request.META.get(
                    "HTTP_REFERER",
                    resolve_url("admin:content_settings_contentsetting_changelist"),
                )
            )

        previews = list(UserPreview.objects.filter(user=request.user))
        preview_context = {
            p.name: (
                p.value
                if not p.user_defined_type
                else (p.value, p.user_defined_type, p.tags, p.help)
            )
            for p in previews
        }

        if not preview_context:
            self.message_user(
                request, _("No preview settings to apply"), messages.WARNING
            )
            return redirect_back()

        apply = True
        for name, value in preview_context.items():
            preview = UserPreview.objects.get(user=request.user, name=name)
            is_userdefined = isinstance(value, tuple)

            setting = ContentSetting.objects.filter(name=name).first()
            if not setting and not is_userdefined:
                UserPreviewHistory.user_record(
                    preview, UserPreviewHistory.STATUS_IGNORED
                )
                preview.delete()
                self.message_user(
                    request,
                    _(
                        "Preview setting %s removed because the setting itself doesn't exist"
                    )
                    % name,
                    messages.WARNING,
                )
                apply = False
                continue

            cs_type = (
                USER_DEFINED_TYPES_INITIAL.get(value[1])
                if is_userdefined
                else get_type_by_name(name)
            )
            if not cs_type:
                UserPreviewHistory.user_record(
                    preview, UserPreviewHistory.STATUS_IGNORED
                )
                preview.delete()
                self.message_user(
                    request,
                    _("Setting Type %s doesn't exist") % name,
                    messages.ERROR,
                )
                apply = False
                continue

            if not cs_type.can_update(request.user):
                self.message_user(
                    request,
                    _("You don't have permissions to update the setting %s") % name,
                    messages.ERROR,
                )
                apply = False
                continue

            try:
                cs_type.validate_value(value[0] if is_userdefined else value)
            except ValidationError as e:
                self.message_user(request, name + ": " + str(e), messages.ERROR)
                apply = False
                continue

            if not is_userdefined and preview.from_value != setting.value:
                if setting.value == preview.value:
                    UserPreviewHistory.user_record(
                        preview, UserPreviewHistory.STATUS_IGNORED
                    )
                    preview.delete()
                    self.message_user(
                        request,
                        _("The value %s was changed already applied") % name,
                        messages.WARNING,
                    )
                else:
                    self.message_user(
                        request,
                        _(
                            "The value %s was changed before applying the preview (check and apply again)"
                        )
                        % name,
                        messages.WARNING,
                    )
                    preview.from_value = setting.value
                    preview.save()
                apply = False
                continue

        if not apply:
            return redirect_back()
        try:
            validate_all_with_context(preview_context)
        except ValidationError as e:
            self.message_user(request, str(e), messages.ERROR)
            return redirect_back()

        for preview in previews:
            preview.apply()
            preview.delete()
        self.message_user(request, _("Preview settings applied"), messages.SUCCESS)

        return redirect_back()

    def reset_preview_on_site(self, request):
        for preview_setting in UserPreview.objects.filter(user=request.user):
            UserPreviewHistory.user_record(
                preview_setting, UserPreviewHistory.STATUS_REMOVED
            )
            preview_setting.delete()

        self.message_user(request, _("Preview settings removed"), messages.SUCCESS)
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

    def import_json_view(self, request):
        """
        Importing Content Settings from different sources using JSON format.

        The sources of the format can be different:
        * JSON file
        * JSON text field
        * ids of HistoryContentSetting records

        The view assumes that all of the data is migrated and values in database are aligned with the types.

        The view has too many lines of code for several reasons:
        * the code includes a lot of check for the json format itself
        * the view inlcudes two actions - peview results and apply results
        * the view inludes logic for user defined types
        """
        raw_json = '{"settings": {}}'
        if request.method == "POST":
            if "json_file" in request.FILES:
                raw_json = request.FILES["json_file"].read().decode("utf-8")
            elif "raw_json" in request.POST:
                raw_json = request.POST["raw_json"]
        else:
            if "history_ids" in request.GET:
                history_ids = request.GET["history_ids"].split(",")
                history_records = HistoryContentSetting.objects.filter(
                    id__in=[int(id) for id in history_ids]
                )
                raw_json = export_to_format(history_records)

        core_context = {
            "title": _("Import Content Settings"),
            "opts": self.model._meta,
        }

        def response_error(message):
            self.message_user(request, message, messages.ERROR)
            return TemplateResponse(
                request,
                "admin/content_settings/contentsetting/import_json.html",
                {**core_context, "raw_json": raw_json},
            )

        try:
            data = json.loads(raw_json)
        except Exception as e:
            return response_error(_("Error JSON parsing: %s") % str(e))

        if "settings" not in data:
            return response_error(_("Wrong JSON format. Settings should be set"))

        if not isinstance(data["settings"], dict):
            return response_error(
                _("Wrong JSON format. Settings should be a dictionary")
            )

        errors, applied, skipped = preview_data(data, request.user)

        preview_on_site_allowed = (
            request.user.has_perm("content_settings.can_preview_on_site")
            and PREVIEW_ON_SITE_SHOW
        )
        if request.POST.get("_import"):
            if (
                "content_settings_form_checksum" in request.POST
                and ADMIN_CHECKSUM_CHECK_BEFORE_SAVE
                and request.POST["content_settings_form_checksum"]
                != content_settings.form_checksum
            ):
                return response_error(
                    _(
                        "The content settings have been changed by another user. Please reload the page and try again. (or disable ADMIN_CHECKSUM_CHECK_BEFORE_SAVE in settings)"
                    )
                )

            if request.POST.get("preview_on_site") and not preview_on_site_allowed:
                return response_error(
                    _(
                        "You don't have permissions to apply preview on site. (Technocally it is only possible if the changes are applied just recently)"
                    )
                )

            applied_names = request.POST.getlist("_applied")
            try:
                import_to(
                    data,
                    [row for row in applied if row["name"] in applied_names],
                    request.POST.get("preview_on_site"),
                    request.user,
                )
            except Exception as e:
                return response_error(str(e))

            prepared_names = {}
            for v in applied:
                if v["name"] not in applied_names:
                    continue

                data_setting = data["settings"][v["name"]]
                if "user_defined_type" in data_setting:
                    prepared_names[v["name"]] = (
                        data_setting["value"],
                        data_setting["user_defined_type"],
                        (
                            set(data_setting["tags"].splitlines())
                            if data_setting["tags"]
                            else set()
                        ),
                        data_setting["help"],
                    )
                else:
                    prepared_names[v["name"]] = v["new_value"]

            if request.POST.get("preview_on_site") and not preview_on_site_allowed:
                return response_error(
                    _(
                        "You don't have permissions to apply preview on site. (Technocally it is only possible if the changes are applied just recently)"
                    )
                )

            for name in applied_names:
                if name not in prepared_names:
                    return response_error(_("Setting %s can not be applied") % name)

            try:
                validate_all_with_context(prepared_names)
            except ValidationError as e:
                return response_error(str(e))

            if request.POST.get("preview_on_site"):
                self.message_user(
                    request,
                    _("Settings successfully imported to preview"),
                    messages.SUCCESS,
                )
            else:
                self.message_user(
                    request, _("Settings successfully imported"), messages.SUCCESS
                )

            return HttpResponseRedirect(
                resolve_url("admin:content_settings_contentsetting_changelist")
            )

        context = {
            **core_context,
            "skipped": skipped,
            "applied": applied,
            "errors": errors,
            "raw_json": json.dumps(data, indent=2),
            "preview_on_site_allowed": preview_on_site_allowed,
        }
        return TemplateResponse(
            request, "admin/content_settings/contentsetting/import_json.html", context
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
                        "error": _("Invalid user_defined_type"),
                        "html": "",
                    }
                )
            else:
                cs_type = cs_type_instance()
        else:
            cs_type = get_type_by_name(request.POST["name"])
        if cs_type is None or cs_type.constant:
            return JsonResponse({"html": "", "error": _("Invalid name")})

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
        "created_on",
        "user_defined_type",
        "name",
        "value",
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
    actions = [
        "export_as_json",
    ]

    def export_as_json(self, request, queryset):
        ids = dict(queryset.order_by("-id").values_list("name", "id"))
        return HttpResponseRedirect(
            reverse("admin:content_settings_import_json")
            + f'?history_ids={",".join(map(str, ids.values()))}'
        )

    export_as_json.short_description = _("Export selected history records as JSON")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, *args):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(ContentSetting, ContentSettingAdmin)
admin.site.register(HistoryContentSetting, HistoryContentSettingAdmin)
