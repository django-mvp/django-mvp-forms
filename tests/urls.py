"""The suite's urlconf: the demo project's routes plus any test-only route."""

from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django_tomselect.autocompletes import AutocompleteModelView

from demo.urls import urlpatterns as demo_urlpatterns
from tests.forms import (
    MaskedDialogForm,
    MaskedLineFormSet,
    MaskedPageForm,
    PartialDatePageForm,
    PartialDatePageLineFormSet,
)

# Where the browser tests' pages ask for IMask. The tests answer the request from
# a copy under tests/data/ and nothing is fetched.
IMASK_ORIGIN = "https://cdn.jsdelivr.net"
IMASK_URL = f"{IMASK_ORIGIN}/npm/imask@7.6.1/dist/imask.min.js"


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


urlpatterns = [
    *demo_urlpatterns,
    path("autocomplete/groups/", GroupAutocomplete.as_view(), name="ac-groups"),
    path("masked/", MaskedPage.as_view(), name="masked"),
    path("dates/", PartialDatePage.as_view(), name="dates"),
    path("dates/three-copies/", PartialDatePage.as_view(copies=3), name="dates-copies"),
    path(
        "dates/without-script/",
        PartialDatePage.as_view(script=False),
        name="dates-bare",
    ),
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
]
