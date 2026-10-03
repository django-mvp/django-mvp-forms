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
    AttachedTextForm,
    ButtonBarForm,
    ChoiceInputsForm,
    ChosenGroupsForm,
    DrawingOverrideForm,
    DrawingsForm,
    DrawingStateForm,
    DrawingTrioForm,
    FieldWithButtonsForm,
    HelperButtonsForm,
    InlineChoicesForm,
    InlineFieldForm,
    InputKindsForm,
    LayoutObjectsForm,
    ModalForm,
    MultiWidgetFieldForm,
    OrderLineFormSet,
    OverrideForm,
    PairForm,
    RangeStateForm,
    RatingAndRangeForm,
    RatingAndRangeOverrideForm,
    RatingAndRangeTrioForm,
    RatingStateForm,
    RowButtonsForm,
    StackedOrderHelper,
    TableOrderHelper,
    TabsForm,
    TextInputsForm,
    TextStatesForm,
    UneditableFieldForm,
)
from mvp_forms.choices import FormChoices, Modifiers
from mvp_forms.templatetags.daisyui import FieldInput


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


class AttachedTextMixin:
    """The forms the attached-text page and the standalone page draw.

    Each form has a prefix of its own, so no id repeats on a page.
    """

    attached_prefix = "attached"
    attached_failing_prefix = "failing-attached"
    attached_failing_data = {"failing-attached-weight": "70"}

    def get_context_data(self, **kwargs):
        """Add the form to post and the one that already fails."""
        kwargs.setdefault(
            "attached_form", AttachedTextForm(prefix=self.attached_prefix)
        )
        kwargs["failing_attached_form"] = AttachedTextForm(
            self.attached_failing_data, prefix=self.attached_failing_prefix, posts=False
        )
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form to post unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form to post bound to what was posted."""
        form = AttachedTextForm(request.POST, prefix=self.attached_prefix)
        return self.render_to_response(self.get_context_data(attached_form=form))


class AttachedTextView(AttachedTextMixin, MVPTemplateView):
    """Text attached to inputs, inside the application shell."""

    template_name = "demo/attached_text.html"
    page_title = "Attached text"
    page_subtitle = "Text drawn before and after an input or a select"
    breadcrumbs = [{"text": "Attached text"}]


class InlineChoicesMixin:
    """The forms the inline-choices page and the standalone page draw.

    Each form has a prefix of its own, so no id repeats on a page.
    """

    inline_prefix = "inline"
    inline_failing_prefix = "failing-inline"
    inline_failing_data = {"failing-inline-size": "huge"}

    def get_context_data(self, **kwargs):
        """Add the form to post and the one that already fails."""
        kwargs.setdefault("inline_form", InlineChoicesForm(prefix=self.inline_prefix))
        kwargs["failing_inline_form"] = InlineChoicesForm(
            self.inline_failing_data, prefix=self.inline_failing_prefix, posts=False
        )
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form to post unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form to post bound to what was posted."""
        form = InlineChoicesForm(request.POST, prefix=self.inline_prefix)
        return self.render_to_response(self.get_context_data(inline_form=form))


class InlineChoicesView(InlineChoicesMixin, MVPTemplateView):
    """Radios and checkboxes in a line, inside the application shell."""

    template_name = "demo/inline_choices.html"
    page_title = "Inline choices"
    page_subtitle = "Radio and checkbox groups with their options along a line"
    breadcrumbs = [{"text": "Inline choices"}]


class FieldWithButtonsMixin:
    """The forms the field-with-buttons page and the standalone page draw.

    Each form has a prefix of its own, so no id repeats on a page.
    """

    buttons_prefix = "buttons"
    buttons_failing_prefix = "failing-buttons"
    buttons_failing_data = {"failing-buttons-search": "", "failing-buttons-code": ""}

    def get_context_data(self, **kwargs):
        """Add the form to post and the one that already fails."""
        kwargs.setdefault(
            "buttons_form", FieldWithButtonsForm(prefix=self.buttons_prefix)
        )
        kwargs["failing_buttons_form"] = FieldWithButtonsForm(
            self.buttons_failing_data, prefix=self.buttons_failing_prefix, posts=False
        )
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form to post unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form to post bound to what was posted."""
        form = FieldWithButtonsForm(request.POST, prefix=self.buttons_prefix)
        return self.render_to_response(self.get_context_data(buttons_form=form))


class FieldWithButtonsView(FieldWithButtonsMixin, MVPTemplateView):
    """A field with buttons joined to its input, inside the application shell."""

    template_name = "demo/field_with_buttons.html"
    page_title = "Field with buttons"
    page_subtitle = "An input with one button or several joined to it"
    breadcrumbs = [{"text": "Field with buttons"}]


class UneditableFieldMixin:
    """The form the uneditable-field page and the standalone page draw.

    The form has a prefix of its own, so no id repeats on a page.
    """

    uneditable_prefix = "uneditable"

    def get_context_data(self, **kwargs):
        """Add the form to post."""
        kwargs.setdefault(
            "uneditable_form", UneditableFieldForm(prefix=self.uneditable_prefix)
        )
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form bound to what was posted."""
        form = UneditableFieldForm(request.POST, prefix=self.uneditable_prefix)
        return self.render_to_response(self.get_context_data(uneditable_form=form))


class UneditableFieldView(UneditableFieldMixin, MVPTemplateView):
    """An uneditable field beside an editable one, inside the application shell."""

    template_name = "demo/uneditable_field.html"
    page_title = "Uneditable field"
    page_subtitle = "A value shown and not changed, beside one that can be"
    breadcrumbs = [{"text": "Uneditable field"}]


class InlineFieldMixin:
    """The forms the inline-field page and the standalone page draw.

    Each form has a prefix of its own, so no id repeats on a page.
    """

    inline_field_prefix = "inline-field"
    inline_field_failing_prefix = "failing-inline-field"
    inline_field_failing_data = {
        "failing-inline-field-email": "",
        "failing-inline-field-city": "",
    }

    def get_context_data(self, **kwargs):
        """Add the form to post and the one that already fails."""
        kwargs.setdefault(
            "inline_field_form", InlineFieldForm(prefix=self.inline_field_prefix)
        )
        kwargs["failing_inline_field_form"] = InlineFieldForm(
            self.inline_field_failing_data,
            prefix=self.inline_field_failing_prefix,
            posts=False,
        )
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form to post unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form to post bound to what was posted."""
        form = InlineFieldForm(request.POST, prefix=self.inline_field_prefix)
        return self.render_to_response(self.get_context_data(inline_field_form=form))


class InlineFieldView(InlineFieldMixin, MVPTemplateView):
    """Fields with no visible label, inside the application shell."""

    template_name = "demo/inline_field.html"
    page_title = "Inline field"
    page_subtitle = "Fields named by their placeholder and no label"
    breadcrumbs = [{"text": "Inline field"}]


class MultiWidgetFieldMixin:
    """The forms the multi-widget-field page and the standalone page draw.

    Each form has a prefix of its own, so no id repeats on a page.
    """

    multi_widget_prefix = "multi-widget"
    multi_widget_failing_prefix = "failing-multi-widget"
    multi_widget_failing_data = {
        "failing-multi-widget-starts_0": "",
        "failing-multi-widget-starts_1": "",
    }

    def get_context_data(self, **kwargs):
        """Add the form to post and the one that already fails."""
        kwargs.setdefault(
            "multi_widget_form", MultiWidgetFieldForm(prefix=self.multi_widget_prefix)
        )
        kwargs["failing_multi_widget_form"] = MultiWidgetFieldForm(
            self.multi_widget_failing_data,
            prefix=self.multi_widget_failing_prefix,
            posts=False,
        )
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form to post unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form to post bound to what was posted."""
        form = MultiWidgetFieldForm(request.POST, prefix=self.multi_widget_prefix)
        return self.render_to_response(self.get_context_data(multi_widget_form=form))


class MultiWidgetFieldView(MultiWidgetFieldMixin, MVPTemplateView):
    """A split date and time with an attribute on each part, inside the shell."""

    template_name = "demo/multi_widget_field.html"
    page_title = "Multi-widget field"
    page_subtitle = "A split date and time with an attribute on each part"
    breadcrumbs = [{"text": "Multi-widget field"}]


class DecoratedFieldsStandaloneView(
    MultiWidgetFieldMixin,
    InlineFieldMixin,
    UneditableFieldMixin,
    FieldWithButtonsMixin,
    InlineChoicesMixin,
    AttachedTextMixin,
    TemplateView,
):
    """The decorated-field forms for a host project without django-mvp or Cotton.

    A post belongs to the form whose submit button it names. One that names none
    binds the attached-text form.
    """

    template_name = "demo/decorated_fields_standalone.html"

    def post(self, request, *args, **kwargs):
        """Bind the form whose submit button was pressed and no other."""
        if f"{self.multi_widget_prefix}-submit" in request.POST:
            return MultiWidgetFieldMixin.post(self, request, *args, **kwargs)
        if f"{self.inline_field_prefix}-submit" in request.POST:
            return InlineFieldMixin.post(self, request, *args, **kwargs)
        if f"{self.uneditable_prefix}-submit" in request.POST:
            return UneditableFieldMixin.post(self, request, *args, **kwargs)
        if f"{self.buttons_prefix}-submit" in request.POST:
            return FieldWithButtonsMixin.post(self, request, *args, **kwargs)
        if f"{self.inline_prefix}-submit" in request.POST:
            return InlineChoicesMixin.post(self, request, *args, **kwargs)
        return AttachedTextMixin.post(self, request, *args, **kwargs)


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


class DrawingsMixin:
    """The form both drawings pages draw, with what it cleaned to once posted.

    A post binds the form and draws the page again. Nothing is saved.
    """

    drawings_prefix = "drawings"
    drawing_names = FieldInput.boolean_drawings
    drawing_states = ("off", "on", "help", "error", "disabled")

    def build_cleaned(self, form):
        """List what a posted form cleaned to, for the page to show.

        Args:
            form: The form to read.

        Returns:
            A list of dicts holding each field's name, label and cleaned value,
            or an empty list when the form is not bound or does not validate.
        """
        if not form.is_valid():
            return []
        return [
            {"name": name, "label": form.fields[name].label, "value": value}
            for name, value in form.cleaned_data.items()
        ]

    def build_drawing_states(self):
        """Build one small form for each drawing in each state.

        Returns:
            A list with a dict for each drawing, holding its name, a heading and a
            list of dicts for its states, each with the state's name and form.
        """
        return [
            {
                "title": drawing,
                "heading": _("%(drawing)s in every state") % {"drawing": drawing},
                "states": [
                    {
                        "title": state,
                        "form": DrawingStateForm(
                            prefix=f"{drawing}-{state}", drawing=drawing, state=state
                        ),
                    }
                    for state in self.drawing_states
                ],
            }
            for drawing in self.drawing_names
        ]

    def build_sizes(self):
        """Build one form of the three drawings for each size a toggle has.

        Returns:
            A list of dicts holding each size's name and form.
        """
        return [
            {
                "title": name,
                "form": DrawingTrioForm(prefix=f"size-{name}", size=name),
            }
            for name in Modifiers.names("size", "toggle")
        ]

    def build_colors(self):
        """Build one form of the three drawings for each colour a toggle has.

        Returns:
            A list of dicts holding each colour's name and form.
        """
        return [
            {
                "title": name,
                "form": DrawingTrioForm(prefix=f"color-{name}", color=name),
            }
            for name in Modifiers.names("color", "toggle")
        ]

    def get_context_data(self, **kwargs):
        """Add the form, what it cleaned to when it was posted, and the states."""
        form = kwargs.setdefault("form", DrawingsForm(prefix=self.drawings_prefix))
        kwargs["drawing_states"] = self.build_drawing_states()
        kwargs["sizes"] = self.build_sizes()
        kwargs["colors"] = self.build_colors()
        kwargs["override_form"] = DrawingOverrideForm(prefix="override")
        kwargs["cleaned"] = self.build_cleaned(form)
        kwargs["prefix"] = self.drawings_prefix
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form bound to what was posted."""
        form = DrawingsForm(request.POST, prefix=self.drawings_prefix)
        return self.render_to_response(self.get_context_data(form=form))


class DrawingsView(DrawingsMixin, MVPTemplateView):
    """A boolean field drawn as a checkbox, a toggle and a switch, in the shell."""

    template_name = "demo/drawings.html"
    page_title = "Checkbox, toggle and switch"
    page_subtitle = "How a boolean field is drawn, chosen in Python"
    breadcrumbs = [{"text": "Checkbox, toggle and switch"}]


class StandaloneDrawingsView(DrawingsMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    template_name = "demo/drawings_standalone.html"


class RatingAndRangeMixin:
    """The forms both rating and range pages draw, with what the first cleaned to.

    A post binds the form and draws the page again. Nothing is saved.
    """

    rating_prefix = "rating"
    range_prefix = "range"
    states = ("help", "error", "disabled")

    def build_cleaned(self, form):
        """List what a posted form cleaned to, for the page to show.

        Args:
            form: The form to read.

        Returns:
            A list of dicts holding each field's name, label and cleaned value,
            or an empty list when the form is not bound or does not validate.
        """
        if not form.is_valid():
            return []
        return [
            {"name": name, "label": form.fields[name].label, "value": value}
            for name, value in form.cleaned_data.items()
        ]

    def build_states(self, prefix, form_class):
        """Build one small form for each state a field is shown in.

        Args:
            prefix: What each form's prefix starts with.
            form_class: The form to build, given a prefix and a state.

        Returns:
            A list of dicts holding each state's name and form.
        """
        return [
            {
                "title": state,
                "form": form_class(prefix=f"{prefix}-{state}", state=state),
            }
            for state in self.states
        ]

    def build_sizes(self):
        """Build one form of a rating and a range for each size they have.

        Returns:
            A list of dicts holding each size's name and form.
        """
        return [
            {
                "title": name,
                "form": RatingAndRangeTrioForm(prefix=f"size-{name}", size=name),
            }
            for name in Modifiers.names("size", "rating")
        ]

    def build_colors(self):
        """Build one form of a rating and a range for each colour they have.

        Returns:
            A list of dicts holding each colour's name and form.
        """
        return [
            {
                "title": name,
                "form": RatingAndRangeTrioForm(prefix=f"color-{name}", color=name),
            }
            for name in Modifiers.names("color", "rating")
        ]

    def get_context_data(self, **kwargs):
        """Add the form, what it cleaned to when it was posted, and the states."""
        form = kwargs.setdefault("form", RatingAndRangeForm(prefix=self.rating_prefix))
        kwargs["rating_states"] = self.build_states(self.rating_prefix, RatingStateForm)
        kwargs["range_states"] = self.build_states(self.range_prefix, RangeStateForm)
        kwargs["sizes"] = self.build_sizes()
        kwargs["colors"] = self.build_colors()
        kwargs["override_form"] = RatingAndRangeOverrideForm(prefix="override")
        kwargs["cleaned"] = self.build_cleaned(form)
        kwargs["prefix"] = self.rating_prefix
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        """Render the page with the form unbound."""
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """Render the page with the form bound to what was posted."""
        form = RatingAndRangeForm(request.POST, prefix=self.rating_prefix)
        return self.render_to_response(self.get_context_data(form=form))


class RatingAndRangeView(RatingAndRangeMixin, MVPTemplateView):
    """A single-choice field drawn as a rating and a number field as a range."""

    template_name = "demo/rating_and_range.html"
    page_title = "Rating and range"
    page_subtitle = "How a rating and a range are drawn, chosen in Python"
    breadcrumbs = [{"text": "Rating and range"}]


class StandaloneRatingAndRangeView(RatingAndRangeMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    template_name = "demo/rating_and_range_standalone.html"


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
