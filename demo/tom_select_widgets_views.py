"""The pages that show this package's Tom Select widgets."""

from crispy_forms.helper import FormHelper
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from mvp.views import MVPTemplateView

from demo.tom_select_widgets_forms import (
    TomSelectWidgetsChosenForm,
    TomSelectWidgetsComparisonForm,
    TomSelectWidgetsContainersForm,
    TomSelectWidgetsForm,
    TomSelectWidgetsGroupsForm,
    TomSelectWidgetsLineFormSet,
    TomSelectWidgetsModalForm,
    TomSelectWidgetsSettingsForm,
    TomSelectWidgetsStateForm,
)
from mvp_forms.choices import Modifiers


class TomSelectWidgetsMixin:
    """The forms both Tom Select widgets pages draw.

    A post binds the form to submit and draws the page again. Nothing is saved.
    """

    prefix = "tom-select-widgets"
    states = (
        ("filled", _("Holding values")),
        ("error", _("In error")),
        ("disabled", _("Disabled")),
    )

    def build_cleaned(self, form):
        """List what a posted form cleaned to, or nothing when it did not validate.

        Several values are shown with a space between.
        """
        if not form.is_valid():
            return []
        return [
            {
                "name": name,
                "label": form.fields[name].label,
                "value": " ".join(value) if isinstance(value, list) else value,
            }
            for name, value in form.cleaned_data.items()
        ]

    def get_context_data(self, **kwargs):
        """Add every form the page draws."""
        form = kwargs.setdefault("form", TomSelectWidgetsForm(prefix=self.prefix))
        context = super().get_context_data(**kwargs)
        # The row "Add a sample" copies: the formset's empty form, drawn alone and
        # without a second management form.
        line = TomSelectWidgetsLineFormSet(prefix="samples")
        line.forms = [line.empty_form]
        line.management_form = []
        lines_helper = FormHelper()
        lines_helper.form_tag = False
        lines_helper.include_media = False
        lines_helper.template = "daisyui/table_inline_formset.html"
        context.update(
            form=form,
            prefix=self.prefix,
            cleaned=self.build_cleaned(form) if form.is_bound else [],
            settings_form=TomSelectWidgetsSettingsForm(prefix="settings"),
            groups_form=TomSelectWidgetsGroupsForm(prefix="groups"),
            lines=TomSelectWidgetsLineFormSet(prefix="samples"),
            line=line,
            lines_helper=lines_helper,
            modal_form=TomSelectWidgetsModalForm(prefix="modal"),
            containers_form=TomSelectWidgetsContainersForm(prefix="containers"),
            states=[
                {
                    "title": title,
                    "form": TomSelectWidgetsStateForm(
                        prefix=f"state-{state}", state=state
                    ),
                }
                for state, title in self.states
            ],
            sizes=[
                {
                    "title": name,
                    "form": TomSelectWidgetsChosenForm(
                        prefix=f"size-{name}", size=name
                    ),
                }
                for name in Modifiers.names("size", "select")
            ],
            colors=[
                {
                    "title": name,
                    "form": TomSelectWidgetsChosenForm(
                        prefix=f"color-{name}", color=name
                    ),
                }
                for name in Modifiers.names("color", "select")
            ],
        )
        return context

    def post(self, request, *args, **kwargs):
        """Bind the form to submit and draw the page again."""
        kwargs["form"] = TomSelectWidgetsForm(request.POST, prefix=self.prefix)
        return self.render_to_response(self.get_context_data(**kwargs))


class TomSelectWidgetsView(TomSelectWidgetsMixin, MVPTemplateView):
    """The widgets, drawn inside the django-mvp shell beside a django-tomselect control."""

    template_name = "demo/tom_select_widgets.html"
    page_title = "Tom Select widgets"
    page_subtitle = (
        "Choice fields drawn as Tom Select controls, with no view behind them"
    )
    breadcrumbs = [{"text": "Third-party widgets"}, {"text": "Tom Select widgets"}]

    def get_context_data(self, **kwargs):
        """Add the form that holds the three kinds of select side by side."""
        context = super().get_context_data(**kwargs)
        context["comparison"] = TomSelectWidgetsComparisonForm(prefix="comparison")
        return context


class StandaloneTomSelectWidgetsView(TomSelectWidgetsMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    template_name = "demo/tom_select_widgets_standalone.html"
