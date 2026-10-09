"""Sidebar navigation for the demo project, registered by ``DemoConfig.ready``."""

# A menu entry whose view_name will not resolve is dropped without an error, so a
# page missing from the sidebar is usually a name that does not match the route.
from flex_menu import MenuItem
from mvp.menus import AppMenu, MenuGroup

AppMenu.extend(
    [
        MenuItem(
            name="overview",
            view_name="overview",
            extra_context={"label": "Overview", "icon": "overview"},
        ),
        MenuItem(
            name="text-inputs",
            view_name="text-inputs",
            extra_context={"label": "Text inputs", "icon": "text-inputs"},
        ),
        MenuItem(
            name="choice-inputs",
            view_name="choice-inputs",
            extra_context={
                "label": "Choice, boolean and file inputs",
                "icon": "choice-inputs",
            },
        ),
        MenuItem(
            name="layout-objects",
            view_name="layout-objects",
            extra_context={"label": "Layout objects", "icon": "layout-objects"},
        ),
        MenuItem(
            name="tabs",
            view_name="tabs",
            extra_context={"label": "Tabs", "icon": "tabs"},
        ),
        MenuItem(
            name="accordion",
            view_name="accordion",
            extra_context={"label": "Accordion", "icon": "accordion"},
        ),
        MenuItem(
            name="modal",
            view_name="modal",
            extra_context={"label": "Modal", "icon": "modal"},
        ),
        MenuItem(
            name="alert",
            view_name="alert",
            extra_context={"label": "Alert", "icon": "alert"},
        ),
        MenuItem(
            name="attached-text",
            view_name="attached-text",
            extra_context={"label": "Attached text", "icon": "attached-text"},
        ),
        MenuItem(
            name="inline-choices",
            view_name="inline-choices",
            extra_context={"label": "Inline choices", "icon": "inline-choices"},
        ),
        MenuItem(
            name="field-with-buttons",
            view_name="field-with-buttons",
            extra_context={"label": "Field with buttons", "icon": "field-with-buttons"},
        ),
        MenuItem(
            name="uneditable-field",
            view_name="uneditable-field",
            extra_context={"label": "Uneditable field", "icon": "uneditable-field"},
        ),
        MenuItem(
            name="inline-field",
            view_name="inline-field",
            extra_context={"label": "Inline field", "icon": "inline-field"},
        ),
        MenuItem(
            name="multi-widget-field",
            view_name="multi-widget-field",
            extra_context={
                "label": "Multi-widget field",
                "icon": "multi-widget-field",
            },
        ),
        MenuItem(
            name="choices",
            view_name="choices",
            extra_context={"label": "Size, colour and variant", "icon": "choices"},
        ),
        MenuItem(
            name="drawings",
            view_name="drawings",
            extra_context={"label": "Checkbox, toggle and switch", "icon": "drawings"},
        ),
        MenuItem(
            name="rating-and-range",
            view_name="rating-and-range",
            extra_context={"label": "Rating and range", "icon": "rating-and-range"},
        ),
        MenuItem(
            name="floating-labels",
            view_name="floating-labels",
            extra_context={"label": "Floating labels", "icon": "floating-labels"},
        ),
        MenuItem(
            name="joined-groups",
            view_name="joined-groups",
            extra_context={"label": "Joined groups", "icon": "joined-groups"},
        ),
        MenuItem(
            name="formset-stacked",
            view_name="formset-stacked",
            extra_context={"label": "Formset, stacked", "icon": "formset-stacked"},
        ),
        MenuItem(
            name="formset-table",
            view_name="formset-table",
            extra_context={"label": "Formset, as a table", "icon": "formset-table"},
        ),
        MenuItem(
            name="themes",
            view_name="themes",
            extra_context={"label": "Themes", "icon": "themes"},
        ),
        MenuGroup(
            name="third-party",
            extra_context={"label": "Third-party widgets"},
            children=[
                MenuItem(
                    name="tomselect",
                    view_name="tomselect",
                    extra_context={"label": "django-tomselect", "icon": "tomselect"},
                ),
            ],
        ),
    ]
)
