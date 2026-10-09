"""Autocomplete views for the django-tomselect page.

They answer from lists held here, so the page needs no model and no data.
"""

from django_tomselect.autocompletes import AutocompleteIterablesView

COUNTRIES = [
    "Argentina", "Australia", "Austria", "Belgium", "Brazil", "Canada", "Chile",
    "China", "Colombia", "Czechia", "Denmark", "Egypt", "Finland", "France",
    "Germany", "Ghana", "Greece", "Iceland", "India", "Indonesia", "Ireland",
    "Italy", "Japan", "Kenya", "Mexico", "Morocco", "Netherlands", "New Zealand",
    "Nigeria", "Norway", "Peru", "Poland", "Portugal", "South Africa",
    "South Korea", "Spain", "Sweden", "Switzerland", "Tanzania", "Turkey",
    "United Kingdom", "United States", "Vietnam",
]  # fmt: skip

LANGUAGES = [
    "Arabic", "Bengali", "Dutch", "English", "French", "German", "Hindi",
    "Indonesian", "Italian", "Japanese", "Korean", "Mandarin", "Polish",
    "Portuguese", "Russian", "Spanish", "Swahili", "Turkish", "Vietnamese",
]  # fmt: skip

KEYWORDS = [
    "geochemistry", "geochronology", "heat flow", "hydrology", "mineralogy",
    "palaeomagnetism", "petrology", "sedimentology", "seismology",
    "structural geology", "tectonics", "volcanology",
    "a keyword long enough to wrap onto a second line in a narrow control",
]  # fmt: skip

ROCKS = {
    "Igneous": [
        "Andesite", "Basalt", "Dacite", "Diorite", "Gabbro", "Granite",
        "Obsidian", "Pegmatite", "Peridotite", "Pumice", "Rhyolite", "Syenite",
    ],
    "Sedimentary": [
        "Breccia", "Chalk", "Chert", "Conglomerate", "Dolomite", "Limestone",
        "Mudstone", "Sandstone", "Shale", "Siltstone",
    ],
    "Metamorphic": [
        "Amphibolite", "Eclogite", "Gneiss", "Hornfels", "Marble", "Phyllite",
        "Quartzite", "Schist", "Slate",
    ],
}  # fmt: skip

UNGROUPED_ROCKS = ["Unknown", "Not a rock"]


class CountryAutocomplete(AutocompleteIterablesView):
    """Countries, for a control that holds one value."""

    iterable = COUNTRIES
    page_size = 12


class LanguageAutocomplete(AutocompleteIterablesView):
    """Languages, for a control that holds several values."""

    iterable = LANGUAGES


class KeywordAutocomplete(AutocompleteIterablesView):
    """Keywords, for a tagging control."""

    iterable = KEYWORDS


class RockAutocomplete(AutocompleteIterablesView):
    """Rocks, each naming the group it is listed under, and two that name none."""

    page_size = 50

    def get_iterable(self):
        """Give each rock its group in ``optgroup``."""
        grouped = [
            {"value": rock, "label": rock, "optgroup": group}
            for group, rocks in ROCKS.items()
            for rock in rocks
        ]
        return grouped + [{"value": rock, "label": rock} for rock in UNGROUPED_ROCKS]

    iterable = True
