"""The demo project's pages."""

import datetime

from django import forms
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

# MVPTemplateView, not TemplateView: it supplies the page title, subtitle and
# breadcrumbs the application shell draws around the content.
from mvp.views import MVPTemplateView

from demo.forms import (
    ORDER_LINE_LIMIT,
    AccordionForm,
    AlertForm,
    ButtonBarForm,
    ChoiceInputsForm,
    ChosenGroupsForm,
    HelperButtonsForm,
    InputKindsForm,
    LayoutObjectsForm,
    ModalForm,
    OrderLineFormSet,
    OverrideForm,
    PairForm,
    RowButtonsForm,
    StackedOrderHelper,
    TableOrderHelper,
    TabsForm,
    TextInputsForm,
    TextStatesForm,
)
from mvp_forms.choices import FormChoices, Modifiers


class OverviewView(MVPTemplateView):
    """What this package is, and what it puts on a page."""

    template_name = "demo/overview.html"
    page_title = "Overview"
    page_subtitle = "What this package puts on a page"
    breadcrumbs = [{"text": "Overview"}]


class StatesMixin:
    """The forms both pages of one kind of input draw.

    A subclass names the form, the values it holds and the values it refuses. Each
    form has a prefix of its own, so no id repeats on the page. A post binds
    ``request.FILES`` as well as ``request.POST``: an upload is validated and then
    dropped with the request, never written to storage.
    """

    form_class = forms.Form
    submit_prefix = "submit"
    submit_initial = {}
    held = {}
    refused = {}

    def build_states(self):
        """Build one form for each state a field can be in.

        Returns:
            A list of dicts holding each state's title and form.
        """
        form_class = self.form_class
        refused = {f"error-{name}": value for name, value in self.refused.items()}
        return [
            {"title": _("Empty"), "form": form_class(prefix="empty")},
            {
                "title": _("Holding a value"),
                "form": form_class(prefix="value", initial=self.held),
            },
            {
                "title": _("Required"),
                "form": form_class(prefix="required", required=True),
            },
            {
                "title": _("With help text"),
                "form": form_class(prefix="help", with_help=True),
            },
            {
                "title": _("With an error"),
                "form": form_class(refused, prefix="error", required=True),
            },
        ]

    def build_submit_form(self, *args):
        """Build the form to submit.

        Args:
            *args: The data and files it is bound to, when there are any.

        Returns:
            The form, every field required and carrying its help text.
        """
        return self.form_class(
            *args,
            prefix=self.submit_prefix,
            initial=self.submit_initial,
            required=True,
            with_help=True,
        )

    def get_context_data(self, **kwargs):
        """Add the submittable form and the forms for each state."""
        kwargs.setdefault("form", self.build_submit_form())
        kwargs["states"] = self.build_states()
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with every form unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the submittable form bound to what was posted."""
        form = self.build_submit_form(request.POST, request.FILES)
        return self.render_to_response(self.get_context_data(form=form))


class TextInputsMixin(StatesMixin):
    """The text inputs both pages draw."""

    form_class = TextInputsForm
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


class TextInputsView(TextInputsMixin, MVPTemplateView):
    """Every text input kind in every state, inside the application shell."""

    template_name = "demo/text_inputs.html"
    page_title = "Text inputs"
    page_subtitle = "Every kind of text input in every state"
    breadcrumbs = [{"text": "Text inputs"}]


class StandaloneTextInputsView(TextInputsMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    template_name = "demo/text_inputs_standalone.html"


class HeldFile:
    """A file a field already holds: the name and address a file input reads.

    The demo has no models and no storage, so this stands where a stored file
    would be.
    """

    name = "report.pdf"
    url = "/media/report.pdf"

    def __str__(self):
        """Return the name a link to the file shows."""
        return self.name


class ChoiceInputsMixin(StatesMixin):
    """The choice, boolean, file and hidden inputs both pages draw.

    Adds a sixth state, disabled, and a small form drawn once disabled and once
    read-only.
    """

    form_class = ChoiceInputsForm
    held = {
        "select": "b",
        "grouped_select": "kale",
        "multiple_select": ["a", "c"],
        "null_boolean": True,
        "date": datetime.date(2026, 10, 3),
        "radio": "b",
        "checkbox": True,
        "checkbox_group": ["a", "c"],
        "clearable_file": HeldFile(),
        "hidden": 7,
    }
    refused = {
        "select": "not a choice",
        "grouped_select": "not a choice",
        "multiple_select": "not a choice",
        "date_year": "2026",
        "date_month": "2",
        "date_day": "31",
        "radio": "not a choice",
        "checkbox_group": "not a choice",
        "hidden": "not a number",
    }
    submit_initial = {"hidden": 7}

    def build_states(self):
        """Build the five states of every page, and a disabled one.

        Returns:
            A list of dicts holding each state's title and form.
        """
        disabled = {
            "title": _("Disabled"),
            "form": self.form_class(
                prefix="disabled", initial=self.held, disabled=True
            ),
        }
        return [*super().build_states(), disabled]

    def build_text_states(self):
        """Build the text input and textarea, disabled and then read-only.

        Returns:
            A list of dicts holding each state's title and form.
        """
        initial = {"text": "Some text", "textarea": "Some lines\nof text"}
        return [
            {
                "title": _("Text input, disabled"),
                "form": TextStatesForm(
                    prefix="textdisabled", initial=initial, disabled=True
                ),
            },
            {
                "title": _("Text input, read-only"),
                "form": TextStatesForm(
                    prefix="textreadonly", initial=initial, read_only=True
                ),
            },
        ]

    def get_context_data(self, **kwargs):
        """Add the disabled and read-only text inputs."""
        kwargs["text_states"] = self.build_text_states()
        return super().get_context_data(**kwargs)


class ChoiceInputsView(ChoiceInputsMixin, MVPTemplateView):
    """Every choice, boolean, file and hidden input in every state, in the shell."""

    template_name = "demo/choice_inputs.html"
    page_title = "Choice, boolean and file inputs"
    page_subtitle = "Every kind of choice, boolean and file input in every state"
    breadcrumbs = [{"text": "Choice, boolean and file inputs"}]


class StandaloneChoiceInputsView(ChoiceInputsMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    template_name = "demo/choice_inputs_standalone.html"


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


class TabsMixin:
    """The forms the tabs page and the standalone page draw.

    Each form has a prefix of its own, so no id repeats on a page.
    """

    tabs_prefix = "tabs"
    tabs_failing_prefix = "failing-tabs"
    failing_data = {
        "failing-tabs-name": "Ada",
        "failing-tabs-street": "12 Example Street",
        "failing-tabs-city": "London",
    }

    def get_context_data(self, **kwargs):
        """Add the form to post and the one that already fails."""
        kwargs.setdefault("tabs_form", TabsForm(prefix=self.tabs_prefix))
        kwargs["failing_tabs_form"] = TabsForm(
            self.failing_data, prefix=self.tabs_failing_prefix, posts=False
        )
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form to post unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form to post bound to what was posted."""
        form = TabsForm(request.POST, prefix=self.tabs_prefix)
        return self.render_to_response(self.get_context_data(tabs_form=form))


class TabsView(TabsMixin, MVPTemplateView):
    """Fields behind tabs, inside the application shell."""

    template_name = "demo/tabs.html"
    page_title = "Tabs"
    page_subtitle = "Fields grouped behind tabs, opening on the first error"
    breadcrumbs = [{"text": "Tabs"}]


class AccordionMixin:
    """The forms the accordion page and the standalone page draw.

    Each form has a prefix of its own, so no id repeats on a page.
    """

    accordion_prefix = "accordion"
    chosen_prefix = "chosen-accordion"

    def get_context_data(self, **kwargs):
        """Add the form to post and the one whose groups the developer chose."""
        kwargs.setdefault("accordion_form", AccordionForm(prefix=self.accordion_prefix))
        kwargs["chosen_form"] = ChosenGroupsForm(prefix=self.chosen_prefix)
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form to post unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form to post bound to what was posted."""
        form = AccordionForm(request.POST, prefix=self.accordion_prefix)
        return self.render_to_response(self.get_context_data(accordion_form=form))


class AccordionView(AccordionMixin, MVPTemplateView):
    """Fields in accordion groups, inside the application shell."""

    template_name = "demo/accordion.html"
    page_title = "Accordion"
    page_subtitle = "Fields grouped in an accordion, opening on the first error"
    breadcrumbs = [{"text": "Accordion"}]


class ModalMixin:
    """The form the modal page and the standalone page draw.

    The form has a prefix, so no id repeats on a page.
    """

    modal_prefix = "modal"

    def get_context_data(self, **kwargs):
        """Add the form whose address fields sit in a modal."""
        kwargs.setdefault("modal_form", ModalForm(prefix=self.modal_prefix))
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form bound to what was posted."""
        form = ModalForm(request.POST, prefix=self.modal_prefix)
        return self.render_to_response(self.get_context_data(modal_form=form))


class ModalView(ModalMixin, MVPTemplateView):
    """Fields in a modal, inside the application shell."""

    template_name = "demo/modal.html"
    page_title = "Modal"
    page_subtitle = "Fields in a modal that a button opens, open on the first error"
    breadcrumbs = [{"text": "Modal"}]


class AlertMixin:
    """The form the alert page and the standalone page draw.

    The form has a prefix, so no id repeats on a page.
    """

    alert_prefix = "alert"

    def get_context_data(self, **kwargs):
        """Add the form whose layout holds the alerts."""
        kwargs.setdefault("alert_form", AlertForm(prefix=self.alert_prefix))
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form bound to what was posted."""
        form = AlertForm(request.POST, prefix=self.alert_prefix)
        return self.render_to_response(self.get_context_data(alert_form=form))


class AlertView(AlertMixin, MVPTemplateView):
    """Alerts between the fields of a form, inside the application shell."""

    template_name = "demo/alert.html"
    page_title = "Alert"
    page_subtitle = "Notices placed between fields, with and without a dismiss control"
    breadcrumbs = [{"text": "Alert"}]


class ContainersStandaloneView(
    AlertMixin, ModalMixin, AccordionMixin, TabsMixin, TemplateView
):
    """The container pages for a host project that has neither django-mvp nor Cotton.

    A post belongs to the form whose submit button it names. One that names none
    binds the tabs form.
    """

    template_name = "demo/containers_standalone.html"

    def post(self, request, *args, **kwargs):
        """Bind the form whose submit button was pressed and no other."""
        if f"{self.alert_prefix}-submit" in request.POST:
            return AlertMixin.post(self, request, *args, **kwargs)
        if f"{self.modal_prefix}-submit" in request.POST:
            return ModalMixin.post(self, request, *args, **kwargs)
        if f"{self.accordion_prefix}-submit" in request.POST:
            return AccordionMixin.post(self, request, *args, **kwargs)
        return TabsMixin.post(self, request, *args, **kwargs)


class ChoicesMixin:
    """The forms both choices pages draw, generated from the tables of Modifiers.

    Each form has a prefix of its own, so no id repeats on the page. None of them
    posts anywhere.
    """

    inputs_size = "md"
    inputs_variant = "ghost"

    def build_sizes(self):
        """Build one small form for each size in the table.

        Returns:
            A list of dicts holding each size's name and form.
        """
        return [
            {
                "title": name,
                "form": PairForm(prefix=f"size-{name}", choices=FormChoices(size=name)),
            }
            for name in Modifiers.names("size", None)
        ]

    def build_colors(self):
        """Build one small form for each colour in the table.

        Returns:
            A list of dicts holding each colour's name and form.
        """
        return [
            {
                "title": name,
                "form": PairForm(
                    prefix=f"color-{name}",
                    choices=FormChoices(color=name, button_color=name),
                ),
            }
            for name in Modifiers.names("color", None)
        ]

    def get_context_data(self, **kwargs):
        """Add the generated forms and the ones that state several choices."""
        kwargs["sizes"] = self.build_sizes()
        kwargs["colors"] = self.build_colors()
        kwargs["inputs_size"] = self.inputs_size
        kwargs["inputs_form"] = InputKindsForm(
            prefix="inputs", choices=FormChoices(size=self.inputs_size)
        )
        kwargs["inputs_variant"] = self.inputs_variant
        kwargs["variant_form"] = InputKindsForm(
            prefix="variant", choices=FormChoices(variant=self.inputs_variant)
        )
        kwargs["buttons_form"] = ButtonBarForm(prefix="buttons")
        kwargs["override_form"] = OverrideForm(prefix="override")
        return super().get_context_data(**kwargs)


class ChoicesView(ChoicesMixin, MVPTemplateView):
    """A size, a colour and a variant stated in Python, inside the shell."""

    template_name = "demo/choices.html"
    page_title = "Size, colour and variant"
    page_subtitle = "Choices stated once for a form, and overridden where needed"
    breadcrumbs = [{"text": "Size, colour and variant"}]


class StandaloneChoicesView(ChoicesMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    template_name = "demo/choices_standalone.html"


class OrderFormsetMixin:
    """The formsets both pages of one layout draw.

    One formset is drawn to submit and one is drawn already bound to lines that
    fail in all three ways. Each has a prefix of its own, so no id repeats on the
    page. A post binds the submitted formset and draws the page again, and nothing
    is saved.
    """

    helper_class = StackedOrderHelper
    submit_prefix = "order"
    failing_prefix = "failing"
    failing_lines = [
        {"item": "pen", "quantity": "0", "unit_price": "2"},
        {"item": "ink", "quantity": "1000", "unit_price": "1000"},
        {"item": "ink", "quantity": "1", "unit_price": "1"},
    ]

    def build_failing_data(self):
        """Build the data the failing formset is bound to.

        Returns:
            A dict of the management form and every line's fields.
        """
        prefix = self.failing_prefix
        data = {
            f"{prefix}-TOTAL_FORMS": str(len(self.failing_lines)),
            f"{prefix}-INITIAL_FORMS": "0",
        }
        for index, line in enumerate(self.failing_lines):
            for name, value in line.items():
                data[f"{prefix}-{index}-{name}"] = value
        return data

    def get_context_data(self, **kwargs):
        """Add the formset to submit, the formset that fails and their helpers."""
        kwargs.setdefault("formset", OrderLineFormSet(prefix=self.submit_prefix))
        kwargs["failing_formset"] = OrderLineFormSet(
            self.build_failing_data(), prefix=self.failing_prefix
        )
        kwargs["helper"] = self.helper_class(self.submit_prefix)
        kwargs["failing_helper"] = self.helper_class(
            self.failing_prefix, form_tag=False
        )
        kwargs["limit"] = ORDER_LINE_LIMIT
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the formset to submit unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the formset to submit bound to what was posted."""
        formset = OrderLineFormSet(request.POST, prefix=self.submit_prefix)
        return self.render_to_response(self.get_context_data(formset=formset))


class StackedFormsetView(OrderFormsetMixin, MVPTemplateView):
    """A formset drawn stacked, inside the application shell."""

    template_name = "demo/formset_stacked.html"
    page_title = "Formset, stacked"
    page_subtitle = "Order lines drawn one after another"
    breadcrumbs = [{"text": "Formset, stacked"}]


class StandaloneStackedFormsetView(OrderFormsetMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    template_name = "demo/formset_stacked_standalone.html"


class TableFormsetView(OrderFormsetMixin, MVPTemplateView):
    """A formset drawn as a table, inside the application shell."""

    helper_class = TableOrderHelper
    template_name = "demo/formset_table.html"
    page_title = "Formset, as a table"
    page_subtitle = "Order lines drawn as the rows of a table"
    breadcrumbs = [{"text": "Formset, as a table"}]


class StandaloneTableFormsetView(OrderFormsetMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    helper_class = TableOrderHelper
    template_name = "demo/formset_table_standalone.html"
