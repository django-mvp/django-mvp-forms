"""Sidebar navigation for the demo project, registered by ``DemoConfig.ready``."""

# A menu entry whose view_name will not resolve is dropped without an error, so a
# page missing from the sidebar is usually a name that does not match the route.
from flex_menu import MenuItem
from mvp.menus import AppMenu

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
            name="formset-stacked",
            view_name="formset-stacked",
            extra_context={"label": "Formset, stacked", "icon": "formset-stacked"},
        ),
        MenuItem(
            name="formset-table",
            view_name="formset-table",
            extra_context={"label": "Formset, as a table", "icon": "formset-table"},
        ),
    ]
)
