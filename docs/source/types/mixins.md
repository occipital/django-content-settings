

# def mix() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L14)

Returns a mix of types. Mixins should go first and the last one should be the main type.

Example:
mix(HTMLMixin, SimpleInt)

# class MinMaxValidationMixin() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L24)

Mixin that validates that value is between min_value and max_value.

Attributes:
min_value: Minimum value. If None, then no minimum value.
max_value: Maximum value. If None, then no maximum value.

# class EmptyNoneMixin() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L59)

Mixin for types that returns None if value is empty string.

# class HTMLMixin() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L72)

Mixin for types that should be displayed in HTML format.
And also returned content should be marked as safe.

# class PositiveValidationMixin(MinMaxValidationMixin) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L88)

Mixin that validates that value is positive.

# class CallToPythonMixin() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L96)

Mixin for callable types, or types that should be called to get the value.

# class GiveCallMixin() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L176)

Mixin for callable types, but result of the call without artuments should be returned.

If suffix is "call" then callable should be returned.

# class MakeCallMixin() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L203)

Mixin for non-callable python objects will be returned as callable given.

Can be usefull when you change callable types to a simple type but don't want to change the code that uses that type.

# class DictSuffixesMixin() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L220)

Mixin that adds suffixes to the type using dictionary of functions.

# class AdminPreviewMenuMixin() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L233)

Mixin that adds a menu to the admin preview.

# class AdminPreviewSuffixesMixin(AdminSuffixesMixinPreview, AdminPreviewMenuMixin) [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L300)

Mixin shows links to preview different suffixes of the value in the admin preview.

# class AdminActionsMixinPreview() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L330)

Mixin that adds actions to the admin preview.