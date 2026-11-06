"""The demo project's pages, written in Markdown and served by django-mvp-sphinx."""

from mvp_sphinx.mounted import DocumentationApp

from demo.settings import BASE_DIR

docs = DocumentationApp(
    build_dir=BASE_DIR / "demo" / "docs" / "_build" / "json",
    source_dir=BASE_DIR / "demo" / "docs",
    name="MVP Forms",
)
