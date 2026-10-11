"""The pages that show django-countries' fields."""

from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from mvp.views import MVPTemplateView

from demo.countries_forms import (
    CountriesForm,
    CountriesSizedForm,
    CountriesStateForm,
)
from mvp_forms.choices import Modifiers


class CountriesMixin:
    """The forms both django-countries pages draw.

    A post binds the form to submit and draws the page again. Nothing is saved.
    """

    prefix = "countries"
    states = (
        ("filled", _("Holding a value")),
        ("error", _("In error")),
        ("disabled", _("Disabled")),
    )

    def build_cleaned(self, form):
        """List what a posted form cleaned to, or nothing when it did not validate.

        Several countries are shown as their codes with a space between.
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
        form = kwargs.setdefault("form", CountriesForm(prefix=self.prefix))
        context = super().get_context_data(**kwargs)
        context.update(
            form=form,
            prefix=self.prefix,
            cleaned=self.build_cleaned(form) if form.is_bound else [],
            states=[
                {
                    "title": title,
                    "form": CountriesStateForm(prefix=f"state-{state}", state=state),
                }
                for state, title in self.states
            ],
            sizes=[
                {
                    "title": name,
                    "form": CountriesSizedForm(prefix=f"size-{name}", size=name),
                }
                for name in Modifiers.names("size", "select")
            ],
        )
        return context

    def post(self, request, *args, **kwargs):
        """Bind the form to submit and draw the page again."""
        kwargs["form"] = CountriesForm(request.POST, prefix=self.prefix)
        return self.render_to_response(self.get_context_data(**kwargs))


class CountriesView(CountriesMixin, MVPTemplateView):
    """django-countries' fields, drawn inside the django-mvp shell."""

    template_name = "demo/countries.html"
    page_title = "django-countries"
    page_subtitle = "Its fields, drawn as daisyUI selects"
    breadcrumbs = [{"text": "Third-party widgets"}, {"text": "django-countries"}]


class StandaloneCountriesView(CountriesMixin, TemplateView):
    """The same page for a host project that has neither django-mvp nor Cotton."""

    template_name = "demo/countries_standalone.html"
