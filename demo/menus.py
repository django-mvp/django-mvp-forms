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
            name="layout-objects",
            view_name="layout-objects",
            extra_context={"label": "Layout objects", "icon": "layout-objects"},
        ),
    ]
)
