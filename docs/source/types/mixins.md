

# mix() [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L14)

Returns a mix of types. Mixins should go first and the last one should be the main type.

Example:
mix(HTMLMixin, SimpleInt)

# Class: MinMaxValidationMixin [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L24)

Mixin that validates that value is between min_value and max_value.

Attributes:
min_value: Minimum value. If None, then no minimum value.
max_value: Maximum value. If None, then no maximum value.

# Class: EmptyNoneMixin [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L59)

Mixin for types that returns None if value is empty string.

# Class: HTMLMixin [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L72)

Mixin for types that should be displayed in HTML format.
And also returned content should be marked as safe.

# Class: PositiveValidationMixin [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L88)

Mixin that validates that value is positive.

# Class: CallToPythonMixin [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L96)

Mixin for callable types, or types that should be called to get the value.

# Class: GiveCallMixin [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L176)

Mixin for callable types, but result of the call without artuments should be returned.

# Class: MakeCallMixin [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L201)

Mixin for non-callable python objects will be returned as callable given.

Can be usefull when you change callable types to a simple type but don't want to change the code that uses that type.

# Class: DictSuffixesMixin [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L218)

Mixin that adds suffixes to the type using dictionary of functions.

# Class: AdminPreviewMenuMixin [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L231)

Mixin that adds a menu to the admin preview.

# Class: AdminPreviewSuffixesMixin [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L298)

Mixin shows links to preview different suffixes of the value in the admin preview.

# Class: AdminActionsMixinPreview [source](https://github.com/occipital/django-content-settings/blob/master/content_settings/types/mixins.py#L328)

Mixin that adds actions to the admin preview.