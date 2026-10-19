"""The views behind the live examples. Every example is one form on one page."""

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView


class ExampleView(FormView):
    """Draw one form, and on a valid post say so and draw it empty again.

    Nothing an example receives is kept.
    """

    template_name = "demo/examples/form.html"
    sent_empty = False

    def get_form_kwargs(self):
        """Bind the form to nothing on arrival when the example opens sent empty."""
        kwargs = super().get_form_kwargs()
        if self.sent_empty and "data" not in kwargs:
            kwargs["data"] = {}
        return kwargs

    def form_valid(self, form):
        """Say the form was accepted and come back to the same address."""
        messages.success(self.request, _("Accepted. Nothing was kept."))
        return redirect(self.request.path)


class FormsetExampleView(ExampleView):
    """Draw one formset with the helper named beside it."""

    template_name = "demo/examples/formset.html"
    helper_class = None

    def get_context_data(self, **kwargs):
        """Add the helper the template hands to the crispy tag."""
        context = super().get_context_data(**kwargs)
        context["helper"] = self.helper_class()
        return context
