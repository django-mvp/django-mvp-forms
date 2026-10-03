"""Print the known-exceptions table and the dimmed pairings.

Run it as `uv run python -m tests.legibility`.
"""

import os

import django


def main() -> None:
    """Print the table the README should hold, then the dimmed pairings."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    django.setup()

    from tests.legibility.catalogue import Catalogue
    from tests.legibility.exceptions import KnownExceptions
    from tests.legibility.themes import Themes

    themes = Themes.shipped()
    measurements = Catalogue.measurements()
    print(KnownExceptions.START)
    print(KnownExceptions.table(measurements, themes))
    print(KnownExceptions.END)
    print()
    print("Disabled controls: dimmed pairings, measured and not held")
    for name, ratios in KnownExceptions.dimmed(measurements, themes).items():
        print(f"\n{name}")
        print(
            "  " + ", ".join(f"{theme} {ratio:.2f}" for theme, ratio in ratios.items())
        )


if __name__ == "__main__":
    main()
