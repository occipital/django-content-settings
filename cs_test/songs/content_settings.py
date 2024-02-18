from content_settings.types.basic import (
    SimpleString,
    SimpleInt,
    SimpleHTML,
    SimpleDecimal,
    SimpleTextPreview,
)
from content_settings.types.datetime import DateString
from content_settings.types.mixins import (
    MinMaxValidationMixin,
    mix,
    DictSuffixesPreviewMixin,
    AdminPreviewActionsMixin,
)
from content_settings.types.array import (
    SimpleStringsList,
    TypedStringsList,
    SplitByFirstLine,
    split_validator_in,
)
from content_settings.types.markup import SimpleYAML
from content_settings.types.each import EachMixin, Keys
from content_settings.types.template import DjangoTemplateHTML, DjangoModelTemplateHTML

from content_settings.context_managers import context_defaults, add_tags
from content_settings import permissions

from .models import Artist

with context_defaults(add_tags(["main"]), fetch_permission=permissions.any):
    TITLE = SimpleString("My Site", help="Title of the site")

    AFTER_TITLE = DjangoTemplateHTML(
        "", help="The html goes right after the title", tags=["html"]
    )

    DAYS_WITHOUT_FAIL = mix(MinMaxValidationMixin, SimpleInt)(
        "5", min_value=0, max_value=10, help="How many days without fail"
    )


FAVORITE_SUBJECTS = SimpleStringsList("", help="my favorive songs subjects")

PRICES = mix(DictSuffixesPreviewMixin, TypedStringsList)(
    "",
    line_type=SimpleDecimal(),
    suffixes={"positive": lambda value: [v for v in value if v >= 0]},
)

START_DATE = DateString("2024-02-11", constant=True)

MY_YAML = mix(EachMixin, SimpleYAML)("", each=Keys(price=SimpleDecimal()))

ARTIST_LINE = DjangoModelTemplateHTML(
    "",
    model_queryset=Artist.objects.all(),
    obj_name="artist",
)

EMAIL_INTRO_TEMPLATE = SplitByFirstLine(
    "",
    split_type={
        "SUBJECT": SimpleTextPreview(""),
        "BODY": DjangoModelTemplateHTML(
            "",
            model_queryset=Artist.objects.all(),
            obj_name="artist",
        ),
    },
    split_key_validator=split_validator_in(["BODY", "SUBJECT"]),
    split_default_key="BODY",
)

HTML_WITH_ACTIONS = mix(AdminPreviewActionsMixin, SimpleHTML)(
    "",
    admin_preview_actions=[
        ("before", lambda resp, *a, **k: resp.before_html("<p>Text Before</p>")),
        ("alert", lambda resp, *a, **k: resp.alert("Let you know, you are good")),
        ("reset to hi", lambda resp, *a, **k: resp.value("Hello world")),
        ("say hi", lambda resp, *a, **k: resp.html("<h1>HI</h1>")),
    ],
    help="Some html with actions",
)
