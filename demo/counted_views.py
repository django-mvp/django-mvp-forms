"""The page that shows the counted multiple select, drawn two ways."""

from django.utils.translation import gettext_lazy as _
from mvp.views import MVPTemplateView

from demo.counted_forms import (
    PlainCountedForm,
    PlainStateForm,
    TomSelectCountedForm,
    TomSelectStateForm,
)


class CountedSelectView(MVPTemplateView):
    """Both drawings side by side. A post binds one form and draws the page again."""

    template_name = "demo/counted_select.html"
    page_title = "Counted multiple select"
    page_subtitle = "A count in the control, a tick beside each chosen option"
    breadcrumbs = [
        {"text": "Custom fields"},
        {"text": "Counted multiple select"},
    ]
    states = (
        ("empty", _("Nothing chosen")),
        ("one", _("One chosen")),
        ("error", _("In error")),
        ("disabled", _("Disabled")),
    )

    def build_cleaned(self, form):
        """List what a posted form cleaned to, or nothing when it did not validate."""
        if not form.is_bound or not form.is_valid():
            return []
        return [
            {
                "name": name,
                "label": form.fields[name].label,
                "value": ", ".join(value) or "—",
            }
            for name, value in form.cleaned_data.items()
        ]

    def get_context_data(self, **kwargs):
        """Add both forms and each state of both."""
        plain = kwargs.pop("plain", None) or PlainCountedForm(prefix="plain")
        tomselect = kwargs.pop("tomselect", None) or TomSelectCountedForm(
            prefix="tomselect"
        )
        context = super().get_context_data(**kwargs)
        context.update(
            plain=plain,
            tomselect=tomselect,
            plain_cleaned=self.build_cleaned(plain),
            tomselect_cleaned=self.build_cleaned(tomselect),
            states=[
                {
                    "title": title,
                    "plain": PlainStateForm(prefix=f"plain-{state}", state=state),
                    "tomselect": TomSelectStateForm(
                        prefix=f"tomselect-{state}", state=state
                    ),
                }
                for state, title in self.states
            ],
        )
        return context

    def post(self, request, *args, **kwargs):
        """Bind whichever form was posted."""
        if "plain-submit" in request.POST:
            kwargs["plain"] = PlainCountedForm(request.POST, prefix="plain")
        else:
            kwargs["tomselect"] = TomSelectCountedForm(request.POST, prefix="tomselect")
        return self.render_to_response(self.get_context_data(**kwargs))
