# ADR 0073 — An autocomplete view for a supported package

**Status:** accepted

## Decision

The package may ship an autocomplete view that answers the requests of a widget of a supported
package, and `CountryAutocomplete` is the first. The host project routes the view to an address
of its own, so the package still ships no URL. The view lives in the one module that imports the
supported package, and it exists only where its own dependency is installed. Page views, form
views and formset handling stay outside the package. Article XII of the constitution says so.

## Why

Article XII said the package ships no views, to keep page views, form views and formset handling
out of it, because those belong to django-mvp. A fetched country control needs a data source that
knows the countries and their flags, and no project can be asked to write one for every control.
An autocomplete view is the data source of a widget, not a page, so it asks nothing of the
article's purpose. Leaving the article as it was would have made the feature unconstitutional.
Routing stays with the host project so the package claims no address.

## Revisit if

The package ships a view that renders a page, or a second supported package needs a view the
host project cannot route itself.
