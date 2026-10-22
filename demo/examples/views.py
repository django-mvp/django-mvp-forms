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
    sent_data = None

    def get_form_kwargs(self):
        """Bind the form on arrival when the example opens already sent."""
        kwargs = super().get_form_kwargs()
        if "data" not in kwargs:
            if self.sent_data is not None:
                kwargs["data"] = self.sent_data
            elif self.sent_empty:
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
    initial = None

    def get_initial(self):
        """Hand the formset the forms it starts out holding."""
        return list(self.initial or [])

    def get_context_data(self, **kwargs):
        """Add the helper the template hands to the crispy tag."""
        context = super().get_context_data(**kwargs)
        context["helper"] = self.helper_class()
        return context


class StoredFilesExampleView(ExampleView):
    """Draw a form whose fields start out holding the files it names.

    A form with a ``sent`` class method is drawn as if it had just been sent
    back with what that returns, so its errors show on the first visit.
    """

    def get_initial(self):
        """Hand the form the files its fields hold."""
        return dict(getattr(self.form_class, "initial_values", {}))

    def get_form_kwargs(self):
        """Bind a form that is shown as sent back, on the first visit too."""
        kwargs = super().get_form_kwargs()
        sent = getattr(self.form_class, "sent", None)
        if sent and self.request.method == "GET":
            kwargs["data"], kwargs["files"] = sent()
        return kwargs
