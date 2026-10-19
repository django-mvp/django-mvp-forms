"""The same forms, drawn as the pack drew them before multi-widget parts joined.

Sketch only: each quantity widget is pointed at a copy of Django's own
multi-widget template, which the pack leaves unjoined.
"""

from demo.examples.third_party.pint import DisabledForm, QuantitiesForm, SizedForm

STACKED = "demo/widgets/multiwidget.html"


def drawn_as_today(form_class):
    """Return a subclass of the form whose multi-widgets draw unjoined."""

    class Today(form_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                field.widget.template_name = STACKED

    Today.__name__ = form_class.__name__
    return Today


QuantitiesToday = drawn_as_today(QuantitiesForm)
SizedToday = drawn_as_today(SizedForm)
DisabledToday = drawn_as_today(DisabledForm)
