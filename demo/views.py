"""The demo project's pages."""

import datetime

from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

# MVPTemplateView, not TemplateView: it supplies the page title, subtitle and
# breadcrumbs the application shell draws around the content.
from mvp.views import MVPTemplateView

from demo.forms import (
    HelperButtonsForm,
    LayoutObjectsForm,
    RowButtonsForm,
    TextInputsForm,
)


class OverviewView(MVPTemplateView):
    """What this package is, and what it puts on a page."""

    template_name = "demo/overview.html"
    page_title = "Overview"
    page_subtitle = "What this package puts on a page"
    breadcrumbs = [{"text": "Overview"}]


class TextInputsMixin:
    """The forms both text inputs pages draw.

    Each form has a prefix of its own, so no id repeats on the page.
    """

    submit_prefix = "submit"
    held = {
        "text": "Some text",
        "email": "name@example.com",
        "url": "https://example.com",
        "number": 42,
        "password": "kept out of the page",
        "date": datetime.date(2026, 10, 3),
        "time": datetime.time(14, 30),
        "date_time": datetime.datetime(2026, 10, 3, 14, 30),
        "textarea": "Some lines\nof text",
    }
    refused = {
        "email": "not an email",
        "url": "not a url",
        "number": "not a number",
        "date": "not a date",
        "time": "not a time",
        "date_time": "not a date and time",
    }

    def build_states(self):
        """Build one form for each state a field can be in.

        Returns:
            A list of dicts holding each state's title and form.
        """
        refused = {f"error-{name}": value for name, value in self.refused.items()}
        return [
            {"title": _("Empty"), "form": TextInputsForm(prefix="empty")},
            {
                "title": _("Holding a value"),
                "form": TextInputsForm(prefix="value", initial=self.held),
            },
            {
                "title": _("Required"),
                "form": TextInputsForm(prefix="required", required=True),
            },
            {
                "title": _("With help text"),
                "form": TextInputsForm(prefix="help", with_help=True),
            },
            {
                "title": _("With an error"),
                "form": TextInputsForm(refused, prefix="error", required=True),
            },
        ]

    def get_context_data(self, **kwargs):
        """Add the submittable form and the forms for each state."""
        kwargs.setdefault(
            "form",
            TextInputsForm(prefix=self.submit_prefix, required=True, with_help=True),
        )
        kwargs["states"] = self.build_states()
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with every form unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the submittable form bound to what was posted."""
        form = TextInputsForm(
            request.POST, prefix=self.submit_prefix, required=True, with_help=True
        )
        return self.render_to_response(self.get_context_data(form=form))


class TextInputsView(TextInputsMixin, MVPTemplateView):
    """Every text input kind in every state, inside the application shell."""

    template_name = "demo/text_inputs.html"
    page_title = "Text inputs"
    page_subtitle = "Every kind of text input in every state"
    breadcrumbs = [{"text": "Text inputs"}]


class StandaloneTextInputsView(TextInputsMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    template_name = "demo/text_inputs_standalone.html"


class LayoutObjectsMixin:
    """The forms both layout objects pages draw.

    Each form has a prefix of its own, so no id repeats on the page.
    """

    submit_prefix = "layout"
    failing_prefix = "failing"
    helper_prefix = "helper"
    small_prefix = "small"
    owner = "Ada Lovelace"

    def get_context_data(self, **kwargs):
        """Add the four forms the page draws and the owner."""
        kwargs.setdefault("form", LayoutObjectsForm(prefix=self.submit_prefix))
        kwargs["failing_form"] = LayoutObjectsForm(
            {}, prefix=self.failing_prefix, form_tag=False
        )
        kwargs["helper_form"] = HelperButtonsForm(prefix=self.helper_prefix)
        kwargs["small_form"] = RowButtonsForm(prefix=self.small_prefix)
        kwargs["owner"] = self.owner
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the submittable form unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the submittable form bound to what was posted."""
        form = LayoutObjectsForm(request.POST, prefix=self.submit_prefix)
        return self.render_to_response(self.get_context_data(form=form))


class LayoutObjectsView(LayoutObjectsMixin, MVPTemplateView):
    """The layout objects, inside the application shell."""

    template_name = "demo/layout_objects.html"
    page_title = "Layout objects"
    page_subtitle = "Fields arranged in groups, rows and columns, and buttons"
    breadcrumbs = [{"text": "Layout objects"}]


class StandaloneLayoutObjectsView(LayoutObjectsMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    template_name = "demo/layout_objects_standalone.html"
