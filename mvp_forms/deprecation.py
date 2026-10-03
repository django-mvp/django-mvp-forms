"""The paths the pack has moved away from, and a host project's templates at them."""

import warnings
from collections.abc import Callable

from django.template import TemplateDoesNotExist

# A path the pack has moved away from, and the path that replaces it, or None when
# nothing does. Empty until a release moves a template (FS-009).
WITHDRAWN: dict[str, str | None] = {}


def host_template(path: str, get_template: Callable[[str], object]) -> str:
    """Return the path to draw where the pack used to draw ``path``.

    The pack no longer ships ``path``, so a template found there is the host
    project's own. It is still drawn, with a ``DeprecationWarning`` naming the old
    path and what replaces it. A host project with nothing there is not warned.

    Args:
        path: A path in ``WITHDRAWN``.
        get_template: Loads a template by path and raises ``TemplateDoesNotExist``
            when there is none. It is the loader of whichever engine or renderer
            would draw the template.

    Returns:
        ``path`` when the host project has a template there, otherwise the path
        that replaces it, or an empty string when nothing does.

    Raises:
        KeyError: ``path`` is not in ``WITHDRAWN``.
    """
    replacement = WITHDRAWN[path]
    try:
        get_template(path)
    except TemplateDoesNotExist:
        return replacement or ""
    if replacement is None:
        warnings.warn(
            f"The template {path!r} is no longer used and nothing replaces it. "
            "Remove your template at that path.",
            DeprecationWarning,
            stacklevel=2,
        )
    else:
        warnings.warn(
            f"The template {path!r} has moved to {replacement!r}. Your template "
            "at the old path is still drawn for this version. Move it.",
            DeprecationWarning,
            stacklevel=2,
        )
    return path
