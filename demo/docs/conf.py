"""Sphinx settings for the demo project's pages."""

project = "MVP Forms"
extensions = ["mvp_sphinx.navigation", "myst_parser"]
source_suffix = {".md": "markdown"}
myst_enable_extensions = ["colon_fence"]
exclude_patterns = ["_build"]
