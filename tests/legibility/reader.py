"""Reads the markup the pack drew into the pairings a person has to make out."""

from dataclasses import dataclass, replace
from typing import ClassVar, NamedTuple

from bs4 import BeautifulSoup, NavigableString, Tag

from tests.legibility.pairings import Element, Ink, Measurement, Pairing

COLOURS = (
    "neutral",
    "primary",
    "secondary",
    "accent",
    "info",
    "success",
    "warning",
    "error",
)
SIZES = ("xs", "sm", "md", "lg", "xl")
FIELDS = ("input", "textarea", "select", "file-input")
CHOICES = ("checkbox", "radio", "toggle")
CONTROLS = (*FIELDS, *CHOICES, "range", "btn")
BUTTON_VARIANTS = ("outline", "dash", "soft", "ghost", "link")
NOT_TEXT_INPUTS = {
    "hidden",
    "checkbox",
    "radio",
    "submit",
    "reset",
    "button",
    "image",
    "file",
}
UNREAD = {"script", "style", "option", "optgroup", "textarea"}

CONTENT = Ink("base-content")
BASE_100 = Ink("base-100")
BASE_200 = Ink("base-200")


class InkRule(NamedTuple):
    """What a class does to the text ink.

    Args:
        mode: `set` states an ink; `fade` keeps a share of the inherited one.
        argument: The ink's name, or the share to keep.
        own: Whether the result is a choice of the pack's that a class could change.
        wins: Whether the class beats every component rule, as a utility does.
        share: The share of a set ink kept, below 1 for a utility with an opacity,
            such as `text-base-content/90`.
    """

    mode: str
    argument: str | float
    own: bool
    wins: bool = False
    share: float = 1.0


class Paint(NamedTuple):
    """What one daisyUI class paints.

    Args:
        ink: What it does to the text ink.
        surface: The colour it gives the surface behind what is inside it.
        control: The control it makes.
        colour: The theme colour it states.
        variant: The variant it states.
        chosen: The theme colour a chosen choice takes.
        tint: The theme colour that tints a card behind its text when chosen.
        lit: The theme colour the text takes once the card around it is chosen.
    """

    ink: InkRule | None = None
    surface: str | None = None
    control: str | None = None
    colour: str | None = None
    variant: str | None = None
    chosen: str | None = None
    tint: str | None = None
    lit: str | None = None


class Uncovered(Exception):
    """A daisyUI class the reader has no row for.

    Args:
        class_name: The class.
        form_state: The drawn state it was found in.
    """

    def __init__(self, class_name: str, form_state: str) -> None:
        super().__init__(f"no row for {class_name!r} in the form state {form_state!r}")
        self.class_name = class_name
        self.form_state = form_state


@dataclass(frozen=True)
class Inherited:
    """What an element passes down to what is inside it.

    Args:
        ink: The text ink.
        surface: The colour behind the element.
        own: Whether the text ink is one the pack chose and a class could change.
        read_text: Whether text found here is read. False inside a developer's alert.
        bordered: Whether a tab here has a bar under it.
        table: Whether the element is inside a table.
        alert: Whether the element is inside an alert.
        chosen: The surface behind the element when the card around it is chosen,
            or None when it is not inside a card.
        lit: The ink the text takes once the card around it is chosen, if it changes.
    """

    ink: Ink = CONTENT
    surface: Ink = BASE_100
    own: bool = False
    read_text: bool = True
    bordered: bool = False
    table: bool = False
    alert: bool = False
    chosen: Ink | None = None
    lit: Ink | None = None


class Reader:
    """Read the pairings in a drawn form from the classes it carries.

    The reader walks the markup top down with two inherited values, the text ink and
    the surface, and `paints` says what each daisyUI class does to them.

    Args:
        form_state: The name of the drawn state, carried by what it reads and by
            `Uncovered`.
        supplied: The classes the developer supplied, which are passed over.
    """

    # What each daisyUI class the pack writes paints, from daisyUI 5.7.47.
    paints: ClassVar[dict[str, Paint]] = {
        "fieldset-legend": Paint(ink=InkRule("set", "base-content", own=False)),
        "label": Paint(ink=InkRule("fade", 0.6, own=True)),
        "text-base-content": Paint(
            ink=InkRule("set", "base-content", own=True, wins=True)
        ),
        # Muted form text.
        "text-base-content/90": Paint(
            ink=InkRule("set", "base-content", own=True, wins=True, share=0.9)
        ),
        "bg-base-200": Paint(surface="base-200"),
        "bg-base-100": Paint(surface="base-100"),
        "card": Paint(surface="base-100"),
        "card-dash": Paint(),
        # A card's icon tile, whose fill turns primary when the card is chosen.
        "group-has-checked:bg-primary": Paint(control="tile"),
        "group-has-checked:text-primary-content": Paint(),
        "border-current": Paint(control="arrow"),
        "group-has-checked:text-base-content": Paint(lit="base-content"),
        "modal-box": Paint(surface="base-100"),
        # A floating label's text sits on a patch of base-100 over the border.
        "floating-label": Paint(surface="base-100"),
        "table": Paint(control="table"),
        "collapse-arrow": Paint(control="arrow"),
        # The bars of a collapsible fieldset's plus and minus.
        "bg-current": Paint(control="arrow"),
        "tabs-border": Paint(variant="border"),
        "tab": Paint(control="tab"),
        "mask-star-2": Paint(control="rating"),
        "alert": Paint(control="alert"),
        "alert-soft": Paint(variant="soft"),
        "status": Paint(control="status"),
        **{control: Paint(control=control) for control in CONTROLS},
        **{
            f"{control}-{colour}": Paint(colour=colour)
            for control in (*CONTROLS, "alert", "status")
            for colour in COLOURS
        },
        **{f"bg-{colour}": Paint(colour=colour) for colour in COLOURS},
        **{
            name: Paint(chosen=colour)
            for colour in COLOURS
            for name in (
                f"checked:bg-{colour}",
                f"checked:border-{colour}",
                f"checked:text-{colour}-content",
                f"has-checked:border-{colour}",
            )
        },
        **{f"has-checked:bg-{colour}/10": Paint(tint=colour) for colour in COLOURS},
        **{f"{control}-ghost": Paint(variant="ghost") for control in FIELDS},
        **{f"btn-{variant}": Paint(variant=variant) for variant in BUTTON_VARIANTS},
    }
    # Classes that paint nothing: structure, links, dividers, sizes and layout.
    silent: ClassVar[frozenset[str]] = frozenset(
        {
            "fieldset",
            "join",
            "join-item",
            "tabs",
            "tab-content",
            "collapse",
            "collapse-title",
            "collapse-content",
            "indicator",
            "indicator-item",
            "modal",
            "modal-action",
            "mask",
            "rating",
            "rating-hidden",
            "link",
            "divider",
            "w-full",
            "flex",
            "flex-col",
            "gap-4",
            "md:flex-row",
            "flex-1",
            "w-auto",
            "min-w-0",
            "flex-wrap",
            "gap-2",
            "mt-4",
            "overflow-x-auto",
            "text-wrap",
            "ms-auto",
            # An image input: its thumbnail's frame, border and mask, and layout.
            "absolute",
            "border",
            "bottom-0",
            "break-words",
            "cursor-pointer",
            "flex-row",
            "gap-1",
            "gap-3",
            "gap-x-4",
            "gap-y-1",
            "group",
            "group-focus-within:opacity-100",
            "group-hover:opacity-100",
            "h-auto",
            "inset-x-0",
            "items-center",
            "justify-center",
            "items-end",
            "items-start",
            "max-h-full",
            "max-w-full",
            "min-w-52",
            "object-contain",
            "object-cover",
            "opacity-0",
            "px-2",
            "py-1",
            "relative",
            "shrink-0",
            "size-8",
            "text-center",
            "text-base",
            "text-sm",
            "text-xs",
            "transition-opacity",
            "w-fit",
            # The two ends of a range, side by side from the small breakpoint up.
            "grid",
            "sm:grid-cols-2",
            # A fieldset's panel and a collapsible fieldset's layout.
            "-translate-x-1/2",
            "-translate-y-1/2",
            "[.peer:checked~legend_&]:hidden",
            "float-left",
            "gap-1.5",
            "h-[0.125em]",
            "hidden",
            "inset-y-0",
            "items-baseline",
            "left-1/2",
            "mb-4",
            "mx-1",
            "p-0",
            "p-4",
            "peer",
            "peer-checked:float-none",
            "peer-checked:grid",
            "peer-checked:ms-3",
            "peer-checked:px-1",
            "peer-checked:py-2",
            "peer-checked:text-xs",
            "peer-checked:w-auto",
            "peer-focus-visible:outline-2",
            # The scale, pills, chips and cards: layout and a card's border.
            "p-3",
            "card-border",
            "checked:before:content-['✓']",
            "font-medium",
            "font-semibold",
            "grid-cols-1",
            "group-open:hidden",
            "group-open:inline",
            "grow",
            "h-11",
            "h-12",
            "has-focus-visible:outline",
            "inline-flex",
            "inline-grid",
            "justify-between",
            "leading-none",
            "min-h-11",
            "min-h-12",
            "place-items-center",
            "pt-1",
            "rounded-3xl",
            "rounded-full",
            "size-5",
            "size-9",
            "sm:grid-cols-1",
            "sm:grid-cols-3",
            "text-end",
            "tracking-wide",
            "uppercase",
            "whitespace-normal",
            "rounded-field",
            "size-[1cap]",
            "sr-only",
            "top-1/2",
            "w-[0.125em]",
            "avatar",
            "avatar-placeholder",
            "rounded-box",
            "border-base-300",
            "border-error",
            "hover:border-primary",
            *(
                f"mask-{shape}"
                for shape in (
                    "squircle",
                    "heart",
                    "hexagon",
                    "hexagon-2",
                    "decagon",
                    "pentagon",
                    "diamond",
                    "square",
                    "circle",
                    "star",
                    "triangle",
                    "triangle-2",
                    "triangle-3",
                    "triangle-4",
                )
            ),
            *(
                f"{control}-{size}"
                for control in (*CONTROLS, "rating")
                for size in SIZES
            ),
        }
    )

    def __init__(self, form_state: str, supplied: frozenset[str] = frozenset()) -> None:
        self.form_state = form_state
        self.supplied = supplied

    def read(self, soup: BeautifulSoup) -> list[Measurement]:
        """Read every pairing in a drawn form.

        Args:
            soup: The parsed markup.

        Returns:
            One measurement per pairing, in document order.

        Raises:
            Uncovered: An element carries a class with no row.
        """
        found: list[Measurement] = []
        self.walk(soup, Inherited(), found)
        return found

    def walk(self, tag: Tag, state: Inherited, found: list[Measurement]) -> None:
        """Read an element and everything inside it.

        Args:
            tag: The element.
            state: What its parent passes down.
            found: The measurements so far, added to.

        Raises:
            Uncovered: The element carries a class with no row.
        """
        names = self.classes(tag)
        if tag.name == "input" and tag.get("type") == "hidden":
            return
        paints = [self.paints[name] for name in names if name in self.paints]
        control = next((paint.control for paint in paints if paint.control), None)
        override = self.override(paints)
        here = self.inherit(tag, state, paints, override)
        element = Element(
            tag.name,
            tag.get("id", ""),
            control or next((n for n in names if n in self.paints), tag.name),
        )
        below = here
        if control in FIELDS:
            below = self.read_field(tag, control, paints, here, element, found)
        elif control in CHOICES:
            self.read_choice(tag, control, paints, here, element, found)
        elif control == "range":
            self.read_range(tag, paints, here, element, found)
        elif control == "rating":
            self.read_star(tag, paints, here, element, found)
        elif control == "btn":
            below = self.read_button(tag, paints, here, element, found)
        elif control == "tab":
            self.read_tab(override, here, element, found)
        elif control == "status":
            colour, _ = self.modifiers(paints)
            ink = Ink(colour) if colour else CONTENT
            self.measure(found, element, "mark", ink, here.surface)
        elif control == "arrow":
            self.measure(found, element, "mark", here.ink, here.surface, own=here.own)
        elif control == "tile":
            self.measure(found, element, "mark", here.ink, here.surface)
            self.measure(found, element, "mark", Ink("primary-content"), Ink("primary"))
        elif control == "alert":
            below = self.read_alert(paints, override, here)
        elif control is None and tag.name in FIELDS:
            self.read_bare(tag, here, element, found)
        elif control is None and any(paint.chosen for paint in paints):
            self.read_card(paints, state, element, found)
        if (
            here.read_text
            and control not in {"btn", "select"}
            and tag.name not in UNREAD
        ):
            self.read_text(tag, here, element, found)
        if tag.name in UNREAD:
            return
        for child in tag.children:
            if isinstance(child, Tag):
                self.walk(child, below, found)

    def classes(self, tag: Tag) -> list[str]:
        """List the classes of an element that the reader has to know.

        Args:
            tag: The element.

        Returns:
            Its classes, without the ones the developer supplied.

        Raises:
            Uncovered: A class is neither painted, silent nor supplied.
        """
        names = [name for name in tag.get("class", []) if name not in self.supplied]
        for name in names:
            if name not in self.paints and name not in self.silent:
                raise Uncovered(name, self.form_state)
        return names

    def override(self, paints: list[Paint]) -> Ink | None:
        """Find the ink a utility class gives, which wins over every component rule.

        Args:
            paints: The paints of the element's classes.

        Returns:
            The ink, or None when no utility states one.
        """
        winning = [paint.ink for paint in paints if paint.ink and paint.ink.wins]
        if not winning:
            return None
        ink = Ink(str(winning[-1].argument))
        return ink if winning[-1].share == 1 else ink.faded(winning[-1].share)

    def inherit(
        self, tag: Tag, state: Inherited, paints: list[Paint], override: Ink | None
    ) -> Inherited:
        """Work out the text ink and the surface at an element.

        Args:
            tag: The element.
            state: What its parent passes down.
            paints: The paints of the element's classes.
            override: The ink a utility class states, if any.

        Returns:
            The state for the element itself.
        """
        ink, own = state.ink, state.own
        for paint in paints:
            rule = paint.ink
            if rule and not rule.wins:
                ink = (
                    Ink(str(rule.argument))
                    if rule.mode == "set"
                    else ink.faded(float(rule.argument))
                )
                own = rule.own
        if tag.name == "thead" and state.table:
            ink, own = CONTENT.faded(0.6), True
        if override:
            ink, own = override, True
        surface, chosen, lit = state.surface, state.chosen, state.lit
        for paint in paints:
            if paint.surface:
                surface, chosen, lit = Ink(paint.surface), None, None
        for paint in paints:
            if paint.tint:
                chosen = Ink(paint.tint).faded(0.1).over(surface)
            if paint.lit:
                lit = Ink(paint.lit)
        return replace(
            state,
            ink=ink,
            own=own,
            surface=surface,
            chosen=chosen,
            lit=lit,
            bordered=state.bordered or any(p.variant == "border" for p in paints),
            table=state.table or any(p.control == "table" for p in paints),
        )

    def modifiers(self, paints: list[Paint]) -> tuple[str | None, str | None]:
        """Find the colour and the variant a control states.

        Args:
            paints: The paints of the element's classes.

        Returns:
            The colour, which is the error colour when that is stated, and the variant.
        """
        colours = [paint.colour for paint in paints if paint.colour]
        variants = [paint.variant for paint in paints if paint.variant]
        colour = "error" if "error" in colours else (colours[0] if colours else None)
        return colour, (variants[0] if variants else None)

    def measure(
        self,
        found: list[Measurement],
        element: Element,
        part: str,
        ink: Ink,
        surface: Ink,
        held: bool = True,
        own: bool = False,
    ) -> None:
        """Add one measurement.

        Args:
            found: The measurements so far, added to.
            element: The element it came from.
            part: What is made out.
            ink: Its colour.
            surface: The colour behind it.
            held: Whether it must meet its figure.
            own: Whether the pack chose its ink.
        """
        pairing = Pairing.of(part, ink, surface)
        found.append(Measurement(self.form_state, element, pairing, held, own))

    def read_text(
        self, tag: Tag, here: Inherited, element: Element, found: list[Measurement]
    ) -> None:
        """Read the text an element holds of its own.

        Args:
            tag: The element.
            here: The state at the element.
            element: The element, for the measurement.
            found: The measurements so far, added to.
        """
        if any(type(c) is NavigableString and c.strip() for c in tag.children):
            self.measure(found, element, "text", here.ink, here.surface, own=here.own)
            if here.chosen is not None:
                ink = here.lit or here.ink
                self.measure(found, element, "text", ink, here.chosen, own=here.own)

    def read_card(
        self,
        paints: list[Paint],
        state: Inherited,
        element: Element,
        found: list[Measurement],
    ) -> None:
        """Read the edge a card takes when it is chosen.

        Args:
            paints: The paints of the element's classes.
            state: What its parent passes down, the surface around the card.
            element: The element, for the measurement.
            found: The measurements so far, added to.
        """
        colour = next(paint.chosen for paint in paints if paint.chosen)
        self.measure(found, element, "mark", Ink(colour), state.surface)

    def read_bare(
        self, tag: Tag, here: Inherited, element: Element, found: list[Measurement]
    ) -> None:
        """Read an input the pack draws with no class of its own.

        Args:
            tag: The element.
            here: The state at the element.
            element: The element, for the measurement.
            found: The measurements so far, added to.
        """
        if tag.get("type") in NOT_TEXT_INPUTS:
            return
        disabled = tag.has_attr("disabled")
        ink = CONTENT.faded(0.4) if disabled else here.ink
        self.measure(found, element, "text", ink, here.surface, not disabled, here.own)
        if tag.get("placeholder"):
            shown = CONTENT.faded(0.2) if disabled else ink.faded(0.5)
            self.measure(
                found, element, "placeholder", shown, here.surface, not disabled
            )

    def read_field(
        self,
        tag: Tag,
        control: str,
        paints: list[Paint],
        here: Inherited,
        element: Element,
        found: list[Measurement],
    ) -> Inherited:
        """Read an input, a textarea, a select or a file input, or the label around one.

        Args:
            tag: The element.
            control: Which of the four it is.
            paints: The paints of the element's classes.
            here: The state at the element.
            element: The element, for the measurement.
            found: The measurements so far, added to.

        Returns:
            The state for what is inside it, standing on its fill.
        """
        colour, variant = self.modifiers(paints)
        wrapper = tag.name not in FIELDS
        disabled = tag.has_attr("disabled") or (
            wrapper and tag.find(attrs={"disabled": True}) is not None
        )
        held = not disabled
        outer = here.surface
        fill = BASE_200 if disabled else (None if variant == "ghost" else BASE_100)
        inner = fill or outer
        if fill:
            edge = (
                BASE_200
                if disabled
                else (Ink(colour) if colour else CONTENT.faded(0.2))
            )
            self.measure(found, element, "border", edge, outer, held)
        ink = here.ink
        if disabled:
            ink = CONTENT.faded(0.2 if control == "file-input" else 0.4)
        if control == "file-input":
            if disabled:
                self.measure(found, element, "text", ink, inner, held)
            elif colour:
                self.measure(
                    found, element, "button text", Ink(f"{colour}-content"), Ink(colour)
                )
            else:
                self.measure(found, element, "button text", CONTENT, BASE_200)
        elif not wrapper:
            self.measure(found, element, "text", ink, inner, held, here.own and held)
            if tag.get("placeholder"):
                shown = CONTENT.faded(0.2) if disabled else ink.faded(0.5)
                self.measure(found, element, "placeholder", shown, inner, held)
        if control == "select" and not self.takes_many(tag):
            self.measure(found, element, "mark", ink, inner, held)
        return replace(here, surface=inner)

    def takes_many(self, tag: Tag) -> bool:
        """Tell whether a select, or the wrapper around one, takes many choices.

        Args:
            tag: The element.

        Returns:
            Whether it is a select with `multiple`, or holds one.
        """
        return tag.has_attr("multiple") or tag.find("select", multiple=True) is not None

    def read_choice(
        self,
        tag: Tag,
        control: str,
        paints: list[Paint],
        here: Inherited,
        element: Element,
        found: list[Measurement],
    ) -> None:
        """Read a checkbox, a radio or a toggle, both off and on.

        Args:
            tag: The element.
            control: Which of the three it is.
            paints: The paints of the element's classes.
            here: The state at the element.
            element: The element, for the measurement.
            found: The measurements so far, added to.
        """
        colour, _ = self.modifiers(paints)
        stated = Ink(colour) if colour else None
        disabled = tag.has_attr("disabled")
        opacity = 0.3 if control == "toggle" else 0.2
        # A choice in a chosen card is chosen too, and stands on the card's tint.
        for outer in dict.fromkeys((here.surface, here.chosen or here.surface)):
            tinted = outer != here.surface
            # Each row: part, ink, the surface it stands on, whether the pack chose it.
            rows: list[tuple[str, Ink, Ink, bool]]
            if control == "checkbox":
                edge = stated or (CONTENT if tinted else CONTENT.faded(0.2))
                rows = [("border", edge, outer, False)]
                if colour:
                    rows.append(("mark", Ink(f"{colour}-content"), Ink(colour), False))
                else:
                    rows.append(("mark", CONTENT, outer, False))
            elif control == "radio":
                text = stated or here.ink
                chosen = here.own and not colour
                rows = [
                    ("border", stated or here.ink.faded(0.2), outer, False),
                    ("border", text, outer, chosen),
                    ("mark", text, BASE_100, chosen),
                ]
                if tinted:
                    rows = rows[1:]
            else:
                lit = stated or CONTENT
                rows = [
                    ("border", CONTENT.faded(0.5), outer, False),
                    ("border", lit, outer, False),
                    ("mark", lit, BASE_100, False),
                ]
            for part, ink, surface, own in dict.fromkeys(rows):
                if disabled:
                    ink, surface = self.dimmed(ink, surface, outer, opacity)
                self.measure(found, element, part, ink, surface, not disabled, own)

    def read_range(
        self,
        tag: Tag,
        paints: list[Paint],
        here: Inherited,
        element: Element,
        found: list[Measurement],
    ) -> None:
        """Read a range: the filled track and the thumb's ring, and the empty track.

        Args:
            tag: The element.
            paints: The paints of the element's classes.
            here: The state at the element.
            element: The element, for the measurement.
            found: The measurements so far, added to.
        """
        colour, _ = self.modifiers(paints)
        outer = here.surface
        ink = Ink(colour) if colour else here.ink
        chosen = here.own and not colour
        rows = [("mark", ink, chosen), ("border", ink.faded(0.1), False)]
        disabled = tag.has_attr("disabled")
        for part, shown, own in rows:
            if disabled:
                shown, _ = self.dimmed(shown, outer, outer, 0.3)
            self.measure(found, element, part, shown, outer, not disabled, own)

    def read_star(
        self,
        tag: Tag,
        paints: list[Paint],
        here: Inherited,
        element: Element,
        found: list[Measurement],
    ) -> None:
        """Read a star of a rating, lit and unlit.

        A lit star is the colour at full strength and an unlit one is a fifth of it,
        whatever the markup says is chosen. daisyUI dims no disabled rating, so a
        disabled star is read as an enabled one and is not held.

        Args:
            tag: The element.
            paints: The paints of the element's classes.
            here: The state at the element.
            element: The element, for the measurement.
            found: The measurements so far, added to.
        """
        colour, _ = self.modifiers(paints)
        ink = Ink(colour) if colour else CONTENT
        held = not tag.has_attr("disabled")
        self.measure(found, element, "mark", ink, here.surface, held)
        self.measure(found, element, "border", ink.faded(0.2), here.surface, held)

    def dimmed(
        self, ink: Ink, surface: Ink, outer: Ink, opacity: float
    ) -> tuple[Ink, Ink]:
        """Draw a part of a control at the opacity a disabled control has.

        Args:
            ink: The part's colour.
            surface: The colour it stands on within the control.
            outer: The colour around the control, which shows through.
            opacity: How much of the control is left.

        Returns:
            The ink and the surface as they are painted.
        """
        if surface == outer:
            return ink.faded(opacity), outer
        return (
            ink.faded(opacity).over(outer),
            surface.faded(opacity).over(outer),
        )

    def read_button(
        self,
        tag: Tag,
        paints: list[Paint],
        here: Inherited,
        element: Element,
        found: list[Measurement],
    ) -> Inherited:
        """Read a button by its colour and variant.

        Args:
            tag: The element.
            paints: The paints of the element's classes.
            here: The state at the element.
            element: The element, for the measurement.
            found: The measurements so far, added to.

        Returns:
            The state for what is inside it, standing on its fill.
        """
        colour, variant = self.modifiers(paints)
        outer = here.surface
        named = Ink(colour) if colour else None
        fill: Ink | None
        if variant in {"outline", "dash", "ghost"}:
            ink, fill = named or CONTENT, None
        elif variant == "soft":
            ink = named or CONTENT
            if colour == "neutral":
                fill = ink.mixed(Ink("neutral-content"), 1 / 11).faded(0.88).over(outer)
            else:
                fill = ink.mixed(BASE_100, 0.08)
        elif variant == "link":
            ink, fill = named or Ink("primary"), None
        elif colour:
            ink, fill = Ink(f"{colour}-content"), Ink(colour)
        else:
            ink, fill = CONTENT, BASE_200
        if tag.has_attr("disabled"):
            ink = CONTENT.faded(0.2)
            fill = (
                None if variant in {"ghost", "link"} else CONTENT.faded(0.1).over(outer)
            )
        override = self.override(paints)
        if override:
            ink = override
        held = not tag.has_attr("disabled")
        self.measure(
            found,
            element,
            "button text",
            ink,
            fill or outer,
            held,
            here.alert or bool(override),
        )
        if held and tag.get("type") in {"radio", "checkbox"}:
            self.read_chosen(paints, variant, ink, outer, element, found)
        return replace(here, surface=fill or outer, read_text=False)

    def read_chosen(
        self,
        paints: list[Paint],
        variant: str | None,
        ink: Ink,
        outer: Ink,
        element: Element,
        found: list[Measurement],
    ) -> None:
        """Read a choice drawn as a button once it is chosen.

        A chosen button is filled in the colour the widget states, and in primary when
        it states none. A button with no fill keeps its text ink and shows the choice
        by its border.

        Args:
            paints: The paints of the element's classes.
            variant: The variant the button states.
            ink: The text ink of the button when it is not chosen.
            outer: The surface around the button.
            element: The element, for the measurement.
            found: The measurements so far, added to.
        """
        stated = next((paint.chosen for paint in paints if paint.chosen), None)
        colour = stated or "primary"
        if stated or variant not in {"outline", "dash", "ghost", "soft", "link"}:
            self.measure(
                found, element, "button text", Ink(f"{colour}-content"), Ink(colour)
            )
        else:
            self.measure(found, element, "button text", ink, outer)
        self.measure(found, element, "mark", Ink(colour), outer)

    def read_tab(
        self,
        override: Ink | None,
        here: Inherited,
        element: Element,
        found: list[Measurement],
    ) -> None:
        """Read a tab chosen and not chosen, and the bar under the chosen one.

        Args:
            override: The ink a utility class states, if any.
            here: The state at the element.
            element: The element, for the measurement.
            found: The measurements so far, added to.
        """
        self.measure(found, element, "text", here.ink, here.surface, own=True)
        unchosen = override or CONTENT.faded(0.5)
        self.measure(found, element, "text", unchosen, here.surface, own=True)
        if here.bordered:
            self.measure(found, element, "mark", here.ink, here.surface, own=True)

    def read_alert(
        self, paints: list[Paint], override: Ink | None, here: Inherited
    ) -> Inherited:
        """Work out an alert's fill and the ink on it.

        The pack writes an alert alone and an error alert with the soft variant. Any
        other colour is the developer's, so what they write in it is not read.

        Args:
            paints: The paints of the element's classes.
            override: The ink a utility class states, if any.
            here: The state at the element.

        Returns:
            The state for what is inside the alert.

        Raises:
            Uncovered: The soft variant is stated with a colour other than error.
        """
        colours = [paint.colour for paint in paints if paint.colour]
        if any(paint.variant == "soft" for paint in paints):
            if colours != ["error"]:
                raise Uncovered("alert-soft", self.form_state)
            ink = override or Ink("error")
            return replace(
                here,
                ink=ink,
                own=True,
                surface=Ink("error").mixed(BASE_100, 0.08),
                alert=True,
            )
        if colours:
            return replace(
                here,
                ink=Ink(f"{colours[0]}-content"),
                surface=Ink(colours[0]),
                read_text=False,
                alert=True,
            )
        return replace(
            here, ink=override or CONTENT, own=False, surface=BASE_200, alert=True
        )
