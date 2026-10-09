"""The pages that show django-tomselect's controls."""

from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from mvp.views import MVPTemplateView

from demo.tomselect_forms import (
    FetchedForm,
    SampleFormSet,
    SampleTableHelper,
    TomSelectForm,
    TomSelectModalForm,
    TomSelectStateForm,
    TomSelectTrioForm,
)
from mvp_forms.choices import Modifiers


class TomSelectMixin:
    """The forms both django-tomselect pages draw.

    A post binds the form to submit and draws the page again. Nothing is saved.
    """

    prefix = "tomselect"
    states = (
        ("filled", _("Holding a value")),
        ("error", _("In error")),
        ("disabled", _("Disabled")),
    )

    def build_cleaned(self, form):
        """List what a posted form cleaned to, or nothing when it did not validate."""
        if not form.is_valid():
            return []
        return [
            {"name": name, "label": form.fields[name].label, "value": value}
            for name, value in form.cleaned_data.items()
        ]

    def get_context_data(self, **kwargs):
        """Add every form the page draws."""
        form = kwargs.setdefault("form", TomSelectForm(prefix=self.prefix))
        modal_form = kwargs.setdefault("modal_form", TomSelectModalForm(prefix="modal"))
        context = super().get_context_data(**kwargs)
        context.update(
            form=form,
            modal_form=modal_form,
            prefix=self.prefix,
            cleaned=self.build_cleaned(form) if form.is_bound else [],
            states=[
                {
                    "title": title,
                    "form": TomSelectStateForm(prefix=f"state-{state}", state=state),
                }
                for state, title in self.states
            ],
            sizes=[
                {
                    "title": name,
                    "form": TomSelectTrioForm(prefix=f"size-{name}", size=name),
                }
                for name in Modifiers.names("size", "select")
            ],
            colors=[
                {
                    "title": name,
                    "form": TomSelectTrioForm(prefix=f"color-{name}", color=name),
                }
                for name in Modifiers.names("color", "select")
            ],
            variants=[
                {
                    "title": name,
                    "form": TomSelectTrioForm(prefix=f"variant-{name}", variant=name),
                }
                for name in Modifiers.names("variant", "select")
            ],
            formset=SampleFormSet(prefix="samples"),
            formset_helper=SampleTableHelper(),
        )
        return context

    def post(self, request, *args, **kwargs):
        """Bind whichever form was posted and draw the page again."""
        if f"{self.prefix}-submit" in request.POST:
            kwargs["form"] = TomSelectForm(request.POST, prefix=self.prefix)
        else:
            kwargs["modal_form"] = TomSelectModalForm(request.POST, prefix="modal")
        return self.render_to_response(self.get_context_data(**kwargs))


class TomSelectView(TomSelectMixin, MVPTemplateView):
    """django-tomselect's controls, drawn inside the django-mvp shell."""

    template_name = "demo/tomselect.html"
    page_title = "django-tomselect"
    page_subtitle = "Its controls, drawn as daisyUI controls"
    breadcrumbs = [{"text": "Third-party widgets"}, {"text": "django-tomselect"}]


class StandaloneTomSelectView(TomSelectMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    template_name = "demo/tomselect_standalone.html"


class TomSelectFetchedView(TemplateView):
    """The form htmx fetches, each time under a prefix of its own."""

    template_name = "demo/tomselect_fetched.html"

    def get_context_data(self, **kwargs):
        """Add the form, with a prefix that no earlier fetch used."""
        context = super().get_context_data(**kwargs)
        count = self.request.GET.get("count", "1")
        prefix = f"fetched-{count}" if count.isdigit() else "fetched-1"
        context["form"] = FetchedForm(prefix=prefix)
        return context


class TomSelectBoostedView(TomSelectMixin, MVPTemplateView):
    """A second page, reached by htmx navigation, that holds controls."""

    template_name = "demo/tomselect_boosted.html"
    page_title = "django-tomselect, reached by htmx"
    page_subtitle = "A page htmx swapped in, whose controls start up on arrival"
    breadcrumbs = [
        {"text": "Third-party widgets"},
        {"text": "django-tomselect", "url": "/tomselect/"},
        {"text": "Reached by htmx"},
    ]
