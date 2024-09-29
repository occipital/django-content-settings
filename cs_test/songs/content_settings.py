from decimal import Decimal

from django.contrib.auth.models import User

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
    AdminPreviewActionsMixin,
    CallToPythonMixin,
    AdminPreviewSuffixesMixin,
    MakeCallMixin,
)
from content_settings.types.array import (
    SimpleStringsList,
    TypedStringsList,
)
from content_settings.types.markup import SimpleYAML, SimpleJSON
from content_settings.types.each import EachMixin, Keys
from content_settings.types.template import (
    DjangoTemplate,
    DjangoTemplateNoArgsHTML,
    DjangoModelTemplateHTML,
    SimpleEval,
    SimpleFunc,
    DjangoTemplateHTML,
    DjangoTemplateNoArgs,
    DjangoTemplateNoArgsHTML,
    SimpleExec,
    SimpleExecNoArgs,
    SimpleExecNoCompile,
    DjangoModelEval,
)
from content_settings.types.validators import call_validator

from content_settings import permissions
from content_settings.defaults.context import defaults, default_tags
from content_settings.defaults.modifiers import add_tags, help_suffix

from .models import Artist

MY_EVAL = SimpleEval("2**4", help="My eval")
MY_JSON = SimpleJSON("""{"a": 1, "b": 2, "c": 3}""", help="My json")

with defaults(add_tags(["main"]), fetch_permission=permissions.any):
    TITLE = SimpleString("My Site", help="Title of the site")

    AFTER_TITLE = DjangoTemplateNoArgsHTML(
        "", help="The html goes right after the title", tags=["html"]
    )

    DAYS_WITHOUT_FAIL = mix(MinMaxValidationMixin, SimpleInt)(
        "5", min_value=0, max_value=10, help="How many days without fail"
    )

with defaults(help_suffix("<i>Try not to update too often</i>")):
    FAVORITE_SUBJECTS = SimpleStringsList("", help="my favorive songs subjects")

    PRICES = mix(AdminPreviewSuffixesMixin, TypedStringsList)(
        "",
        line_type=SimpleDecimal(),
        suffixes={"positive": lambda value: [v for v in value if v >= 0]},
    )

START_DATE = DateString("2024-02-11", constant=True)

MY_YAML = mix(EachMixin, SimpleYAML)("", each=Keys(price=SimpleDecimal()))

ARTIST_LINE = DjangoModelTemplateHTML(
    "",
    template_model_queryset=Artist.objects.all(),
    template_object_name="artist",
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

WELCOME_FUNC = SimpleFunc(
    "Welcome {name}",
    call_func=lambda name, prepared: prepared.format(name=name),
    validators=(call_validator("Aex"),),
    version="2",
)

TOTAL_INT_FUNC = mix(CallToPythonMixin, SimpleInt)(
    "10",
    call_func=lambda value, prepared: prepared + value,
    validators=(call_validator(20),),
)

FEE_COOF = SimpleDecimal("10", constant=True)

with default_tags({"templates"}):
    DJANGO_TEMPLATE = DjangoTemplate("Hi")

    SIMPLE_FUNCTON = SimpleFunc(
        "HI",
        call_func=lambda prepared: prepared * 5,
        validators=(call_validator(),),
    )

    DJANGO_TEMPLATE_HTML = DjangoTemplateHTML("<b>HI</b>")

    DJANGO_TEMPLATE_NO_ARGS = DjangoTemplateNoArgs("<b>HI</b>")

    DJANGO_TEMPLATE_NO_ARGS_HTML = DjangoTemplateNoArgsHTML("<b>HI</b>")

    def str_type_validator(value):
        ret = value()
        if not isinstance(ret, str):
            raise ValueError("Value must be a string")

    SIMPLE_EVAL = SimpleEval("'10 * 5'", validators=(str_type_validator,), version="2")

    SIMPLE_EXEC = SimpleExec(
        """
fee = value * Decimal("0.1")
result = value - fee
    """,
        template_args_default={"value": Decimal("0.0")},
        template_static_data={"Decimal": Decimal},
        template_return=("result", "fee"),
    )

    SIMPLE_EXEC_NO_ARGS = SimpleExecNoArgs(
        """
fee = Decimal("0.1")
result = Decimal("0.2")
    """,
        template_static_data={"Decimal": Decimal},
        template_return=("result", "fee"),
    )

    SIMPLE_EXEC_NO_COMPILE = SimpleExecNoCompile(
        """
fee = Decimal("0.1")
result = Decimal("0.2")
    """,
        template_static_data={"Decimal": Decimal},
        template_return="result",
        version="2",
    )

    TEXT_MAKE_CALL = mix(MakeCallMixin, SimpleDecimal)("100", version="2")

    USER_MODEL_EVAL = DjangoModelEval(
        "100", template_object_name="user", template_model_queryset=User.objects.all()
    )
