"""The suite's urlconf: the demo project's routes plus any test-only route."""

import json

from django.contrib.auth.models import Group
from django.http import HttpResponse, JsonResponse
from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django_tomselect.autocompletes import AutocompleteModelView

from demo.urls import urlpatterns as demo_urlpatterns
from mvp_forms.widgets import TomSelect
from tests.forms import (
    CharactersLeftDialogForm,
    CharactersLeftLineForm,
    CharactersLeftLineFormSet,
    CharactersLeftPageForm,
    ChoiceFoldLineForm,
    ChoiceFoldLineFormSet,
    ChoiceLongLabelForm,
    ChoiceWidgetsForm,
    ImagePageForm,
    MaskedDialogForm,
    MaskedLineFormSet,
    MaskedPageForm,
    PartialDatePageForm,
    PartialDatePageLineFormSet,
    TomSelectDialogForm,
    TomSelectForm,
    TomSelectLineFormSet,
    TomSelectPageForm,
    TomSelectTagsForm,
    UnlabelledSelectsForm,
)

# Where the browser tests' pages ask for IMask. The tests answer the request from
# a copy under tests/data/ and nothing is fetched.
IMASK_ORIGIN = "https://cdn.jsdelivr.net"
IMASK_URL = f"{IMASK_ORIGIN}/npm/imask@7.6.1/dist/imask.min.js"
# Where a browser test's page asks for a Tom Select of its own, as a project that
# loads one already would, and for django-tomselect's script, which carries its
# own copy. The tests answer the first from a file under tests/data/.
TOM_SELECT_URL = (
    "https://cdn.jsdelivr.net/npm/tom-select@2.5.2/dist/js/tom-select.complete.min.js"
)
DJANGO_TOMSELECT_URL = "/static/django_tomselect/js/django-tomselect.min.js"
# Where the boosted pages ask for htmx. The tests answer it from a file.
HTMX_URL = "https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"


class GroupAutocomplete(AutocompleteModelView):
    """Groups, for the django-tomselect widgets that read a model."""

    model = Group
    search_lookups = ["name__icontains"]
    value_fields = ["id", "name"]
    skip_authorization = True


@method_decorator(csrf_exempt, name="dispatch")
class MaskedPage(TemplateView):
    """A page of masked fields, which answers a post with the entries it got."""

    template_name = "tests/masked_page.html"
    imask = True
    copies = 1
    policy = ""
    cleaned = False

    def get_context_data(self, **kwargs):
        """Draw the form, with its initial values taken from the query string."""
        return super().get_context_data(
            form=MaskedPageForm(initial=self.request.GET.dict()),
            dialog=MaskedDialogForm(),
            line=MaskedLineFormSet().empty_form,
            imask=self.imask,
            imask_url=IMASK_URL,
            copies=range(self.copies),
            **kwargs,
        )

    def render_to_response(self, context, **response_kwargs):
        """State the page's Content-Security-Policy, where it has one."""
        response = super().render_to_response(context, **response_kwargs)
        if self.policy:
            response["Content-Security-Policy"] = self.policy
        return response

    def post(self, request, *args, **kwargs):
        """Return each entry of the post as JSON, or what each field cleaned to."""
        if self.cleaned:
            form = MaskedPageForm(request.POST)
            form.full_clean()
            return JsonResponse(
                {name: str(value) for name, value in form.cleaned_data.items()}
            )
        return JsonResponse({name: request.POST.getlist(name) for name in request.POST})


@method_decorator(csrf_exempt, name="dispatch")
class CharactersLeftPage(TemplateView):
    """A page of fields with the line, which answers a post with how it cleaned."""

    template_name = "tests/characters_left_page.html"
    script = True
    copies = 1

    def get_context_data(self, **kwargs):
        """Draw the form, with its initial values taken from the query string."""
        return super().get_context_data(
            form=CharactersLeftPageForm(initial=self.request.GET.dict()),
            dialog=CharactersLeftDialogForm(),
            line=CharactersLeftLineFormSet().empty_form,
            script=self.script,
            htmx_url=HTMX_URL,
            copies=range(self.copies),
            **kwargs,
        )

    def post(self, request, *args, **kwargs):
        """Return whether the form was valid, its error codes and what it cleaned."""
        form = CharactersLeftPageForm(request.POST)
        form.full_clean()
        return JsonResponse(
            {
                "errors": {
                    name: [error.code for error in errors]
                    for name, errors in form.errors.as_data().items()
                },
                "note": form.cleaned_data.get("note"),
            }
        )


class CharactersLeftFragment(TemplateView):
    """A form with the line, as htmx swaps it into a page."""

    template_name = "tests/characters_left_fragment.html"

    def get_context_data(self, **kwargs):
        """Draw one field."""
        return super().get_context_data(form=CharactersLeftLineForm(), **kwargs)


class ImagePage(TemplateView):
    """A page of image inputs, drawn by the pack, with or without their script."""

    template_name = "tests/image_page.html"
    script = True

    def get_context_data(self, **kwargs):
        """Draw the form."""
        return super().get_context_data(
            form=ImagePageForm(), script=self.script, **kwargs
        )


@method_decorator(csrf_exempt, name="dispatch")
class PartialDatePage(TemplateView):
    """A page of three-part dates, which answers a post with what the form made."""

    template_name = "tests/partial_date_page.html"
    script = True
    copies = 1

    def get_context_data(self, **kwargs):
        """Draw the form, bound when the query string says it was sent."""
        entries = self.request.GET.dict()
        bound = entries.pop("bound", None)
        form = PartialDatePageForm(entries) if bound else PartialDatePageForm()
        if not bound:
            form.initial = entries
        return super().get_context_data(
            form=form,
            line=PartialDatePageLineFormSet().empty_form,
            script=self.script,
            copies=range(self.copies),
            **kwargs,
        )

    def post(self, request, *args, **kwargs):
        """Return the entries of the post, what the form cleaned and its error codes."""
        form = PartialDatePageForm(request.POST)
        form.full_clean()
        return JsonResponse(
            {
                "entries": {name: request.POST.getlist(name) for name in request.POST},
                "cleaned": {name: str(v) for name, v in form.cleaned_data.items()},
                "errors": {
                    name: [error.code for error in errors]
                    for name, errors in form.errors.as_data().items()
                },
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class ChoicePage(TemplateView):
    """A page of every choice widget, which answers a valid post with what it got."""

    template_name = "tests/choice_page.html"
    script = True
    copies = 1
    htmx = False

    def get_context_data(self, **kwargs):
        """Draw the form, bound when the query string says it was sent."""
        entries = self.request.GET.copy()
        bound = entries.pop("bound", None)
        form = ChoiceWidgetsForm(entries) if bound else ChoiceWidgetsForm()
        return super().get_context_data(
            form=form,
            line=ChoiceFoldLineFormSet().empty_form,
            long=ChoiceLongLabelForm(),
            script=self.script,
            copies=range(self.copies),
            htmx=self.htmx,
            htmx_url=HTMX_URL,
            **kwargs,
        )

    def post(self, request, *args, **kwargs):
        """Answer with the entries when the form is valid, else draw it again."""
        form = ChoiceWidgetsForm(request.POST)
        if not form.is_valid():
            context = self.get_context_data()
            context["form"] = form
            return self.render_to_response(context)
        return JsonResponse(
            {
                "entries": {name: request.POST.getlist(name) for name in request.POST},
                "cleaned": {name: str(v) for name, v in form.cleaned_data.items()},
            }
        )


def choice_fragment(request):
    """Return the fields of one line of a formset, as a form swapped in by htmx."""
    return HttpResponse(ChoiceFoldLineForm().as_div())


@method_decorator(csrf_exempt, name="dispatch")
class ChoicesPage(TemplateView):
    """A page of Tom Select widgets, which answers a post with the entries it got."""

    template_name = "tests/tomselect_page.html"
    # A Tom Select the page loads itself, after the form's media or before it.
    tomselect_url = None
    first = False
    # Only the script that starts the controls, and not the rest of the media.
    script_only = False
    copies = 1
    policy = ""
    foreign = False
    refused = False

    def get_context_data(self, **kwargs):
        """Draw the form, with its initial values taken from the query string."""
        return super().get_context_data(
            form=TomSelectPageForm(initial=self.request.GET.dict()),
            foreign=TomSelectForm() if self.foreign else None,
            line=TomSelectLineFormSet().empty_form,
            dialog=TomSelectDialogForm(),
            tomselect_url=self.tomselect_url,
            first=self.first,
            script_only=self.script_only,
            copies=range(self.copies),
            refused=self.refused,
            **kwargs,
        )

    def render_to_response(self, context, **response_kwargs):
        """State the page's Content-Security-Policy, where it has one."""
        response = super().render_to_response(context, **response_kwargs)
        if self.policy:
            response["Content-Security-Policy"] = self.policy
        return response

    def post(self, request, *args, **kwargs):
        """Return each entry of the post as JSON."""
        return JsonResponse({name: request.POST.getlist(name) for name in request.POST})


class TemplatedPage(TemplateView):
    """A page whose select states an option template and an item template."""

    template_name = "tests/templated_page.html"

    def get_context_data(self, **kwargs):
        """Write the settings the select holds, and the script's media."""
        template = '<p><img src="${data.flag}"><i>${data.text}</i></p>'
        return super().get_context_data(
            templated=json.dumps({"render": {"option": template, "item": template}}),
            media=TomSelect().media,
            **kwargs,
        )


class UnlabelledPage(TemplateView):
    """A page of Tom Select controls drawn by the pack with the labels off."""

    template_name = "tests/tomselect_unlabelled_page.html"

    def get_context_data(self, **kwargs):
        """Draw the form's selects, leaving out django-tomselect's."""
        return super().get_context_data(
            form=UnlabelledSelectsForm(layout=["plain", "single", "counted"]),
            **kwargs,
        )


class BoostedPage(TemplateView):
    """One of two pages whose selects share an id, each linking to the other."""

    template_name = "tests/tomselect_boosted_page.html"
    other = ""

    def get_context_data(self, **kwargs):
        """Draw the form and the address of the other page."""
        return super().get_context_data(
            form=TomSelectTagsForm(),
            other=self.other,
            htmx_url=HTMX_URL,
            **kwargs,
        )


# The demo's pages answer every address nothing before them claims, so the
# suite's own routes come first.
urlpatterns = [
    path("autocomplete/groups/", GroupAutocomplete.as_view(), name="ac-groups"),
    path("masked/", MaskedPage.as_view(), name="masked"),
    path("characters-left/", CharactersLeftPage.as_view(), name="characters-left"),
    path(
        "characters-left/two-scripts/",
        CharactersLeftPage.as_view(copies=2),
        name="characters-left-twice",
    ),
    path(
        "characters-left/without-script/",
        CharactersLeftPage.as_view(script=False),
        name="characters-left-bare",
    ),
    path(
        "characters-left/fragment/",
        CharactersLeftFragment.as_view(),
        name="characters-left-fragment",
    ),
    path("images/", ImagePage.as_view(), name="images"),
    path("images/without-script/", ImagePage.as_view(script=False), name="images-bare"),
    path("dates/", PartialDatePage.as_view(), name="dates"),
    path("dates/three-copies/", PartialDatePage.as_view(copies=3), name="dates-copies"),
    path(
        "dates/without-script/",
        PartialDatePage.as_view(script=False),
        name="dates-bare",
    ),
    path("choice-widgets/", ChoicePage.as_view(), name="choice-widgets"),
    path(
        "choice-widgets/without-script/",
        ChoicePage.as_view(script=False),
        name="choice-widgets-bare",
    ),
    path(
        "choice-widgets/three-copies/",
        ChoicePage.as_view(copies=3),
        name="choice-widgets-copies",
    ),
    path(
        "choice-widgets/htmx/",
        ChoicePage.as_view(htmx=True),
        name="choice-widgets-htmx",
    ),
    path("choice-widgets/fragment/", choice_fragment, name="choice-fragment"),
    path("masked/three-copies/", MaskedPage.as_view(copies=3), name="masked-copies"),
    path("masked/cleaned/", MaskedPage.as_view(cleaned=True), name="masked-cleaned"),
    path("masked/without-imask/", MaskedPage.as_view(imask=False), name="masked-bare"),
    path(
        "masked/without-imask/cleaned/",
        MaskedPage.as_view(imask=False, cleaned=True),
        name="masked-bare-cleaned",
    ),
    path(
        "masked/strict-policy/",
        MaskedPage.as_view(policy=f"script-src 'self' {IMASK_ORIGIN}"),
        name="masked-strict",
    ),
    path("choices-page/", ChoicesPage.as_view(), name="choices-page"),
    path(
        "choices-page/three-copies/",
        ChoicesPage.as_view(copies=3),
        name="choices-page-copies",
    ),
    path("templated-page/", TemplatedPage.as_view(), name="templated-page"),
    path(
        "choices-page/without-tom-select/",
        ChoicesPage.as_view(script_only=True),
        name="choices-page-bare",
    ),
    path(
        "choices-page/own-tom-select-first/",
        ChoicesPage.as_view(tomselect_url=TOM_SELECT_URL, first=True),
        name="choices-page-own-first",
    ),
    path(
        "choices-page/own-tom-select-after/",
        ChoicesPage.as_view(tomselect_url=TOM_SELECT_URL),
        name="choices-page-own-after",
    ),
    path(
        "choices-page/django-tomselect/",
        ChoicesPage.as_view(tomselect_url=DJANGO_TOMSELECT_URL),
        name="choices-page-django-tomselect",
    ),
    path(
        "choices-page/django-tomselect-first/",
        ChoicesPage.as_view(
            tomselect_url=DJANGO_TOMSELECT_URL, first=True, foreign=True
        ),
        name="choices-page-django-tomselect-first",
    ),
    path(
        "choices-page/strict-policy/",
        ChoicesPage.as_view(policy="script-src 'self'"),
        name="choices-page-strict",
    ),
    path(
        "choices-page/with-django-tomselect-field/",
        ChoicesPage.as_view(foreign=True),
        name="choices-page-foreign",
    ),
    path(
        "choices-page/with-refused-select/",
        ChoicesPage.as_view(refused=True),
        name="choices-page-refused",
    ),
    path(
        "choices-page/styled/",
        ChoicesPage.as_view(
            template_name="tests/tomselect_styled_page.html",
            tomselect_url=DJANGO_TOMSELECT_URL,
            foreign=True,
        ),
        name="choices-page-styled",
    ),
    path("choices-page/unlabelled/", UnlabelledPage.as_view(), name="unlabelled"),
    path(
        "boosted/list/",
        BoostedPage.as_view(other="boosted-new"),
        name="boosted-list",
    ),
    path(
        "boosted/new/",
        BoostedPage.as_view(other="boosted-list"),
        name="boosted-new",
    ),
    *demo_urlpatterns,
]
