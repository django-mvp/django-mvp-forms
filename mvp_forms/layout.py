"""The layout objects a form uses, beyond those of ``crispy_forms.layout``.

``Join`` is the package's own, and ``Fieldset`` is django-crispy-forms' own with
the option to collapse. The others come from django-crispy-forms'
``crispy_forms.bootstrap`` module, which is named for the framework its own
templates were written for, and are passed through unchanged so that a form
imports them from here. The ``daisyui`` template pack draws each of them.
"""

from dataclasses import dataclass
from html import unescape
from typing import Any, cast

from crispy_forms.bootstrap import (
    Accordion,
    AccordionGroup,
    Alert,
    FormActions,
    InlineCheckboxes,
    InlineField,
    InlineRadios,
    Modal,
    StrictButton,
    Tab,
    TabHolder,
    UneditableField,
)
from crispy_forms.layout import HTML, BaseInput, Field, LayoutObject
from crispy_forms.layout import Fieldset as CrispyFieldset
from crispy_forms.utils import TEMPLATE_PACK, flatatt, render_field
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import SafeData, SafeString
from django.utils.text import slugify

from mvp_forms.choices import INHERIT, Choice, FormChoices, InvalidChoice, Modifiers

__all__ = [
    "Accordion",
    "AccordionGroup",
    "Alert",
    "Fieldset",
    "FormActions",
    "GroupButton",
    "GroupText",
    "InlineCheckboxes",
    "InlineField",
    "InlineRadios",
    "InvalidMember",
    "Join",
    "Member",
    "Modal",
    "StrictButton",
    "Tab",
    "TabHolder",
    "UneditableField",
]


class InvalidMember(ValueError):
    """Something in a joined group that cannot be joined.

    Args:
        member: The name of the field, when its widget is not an input or a
            select, or the class name of the layout object, when the group holds
            anything but field names, ``Field``, ``Choice``, buttons and
            ``HTML``.
    """

    def __init__(self, member: str) -> None:
        self.member = member
        super().__init__(
            f"{member!r} cannot be a member of a joined group: only a field drawn "
            "as an input or a select can, named alone, in a Field or in a Choice, "
            "a button and HTML"
        )


@dataclass(frozen=True)
class Member:
    """One field of a joined group, with what the group says about it.

    Args:
        name: The field's name.
        attrs: The attributes of the ``Field`` that held the name, as
            django-crispy-forms keeps them. Empty for a bare name.
        choice: The ``Choice`` around the name, merged over any ``Choice``
            further out in the group, or None when none is.
    """

    name: str
    attrs: dict[str, Any]
    choice: Choice | None

    def field(self, template: str) -> Field:
        """Return a ``Field`` that draws the member with a template.

        Args:
            template: The template that draws one member.

        Returns:
            A ``Field`` for the name, with the attributes the group gave it.
        """
        field = Field(self.name, template=template)
        field.attrs.update(self.attrs)
        return field


@dataclass(frozen=True)
class GroupButton:
    """One button of a joined group, with the choice the group states for it.

    Args:
        button: The ``StrictButton``, ``Submit``, ``Button`` or ``Reset``.
        choice: The ``Choice`` around the button in the group, merged over any
            ``Choice`` further out in the group, or None when none is.
    """

    button: Any
    choice: Choice | None

    @staticmethod
    def accepts(item: Any) -> bool:
        """Whether a layout object is a button a joined group can hold.

        A ``Hidden`` is an input of django-crispy-forms like a ``Submit`` and is
        not a button, so it is not one.

        Args:
            item: The layout object.
        """
        if isinstance(item, StrictButton):
            return True
        return isinstance(item, BaseInput) and item.input_type != "hidden"


@dataclass(frozen=True)
class GroupText:
    """Text of a joined group, with the choice the group states for it.

    Args:
        text: The ``HTML`` layout object that holds the text.
        choice: The ``Choice`` around the text in the group, merged over any
            ``Choice`` further out in the group, or None when none is.
    """

    # The component the text is drawn as, so that it is framed and sized as the
    # inputs beside it are.
    component = "input"
    template = "%s/layout/join_text.html"

    text: HTML
    choice: Choice | None

    def classes(self, choices: FormChoices) -> list[str]:
        """Return the classes of the size, colour and variant the text takes.

        The text takes them as an input of the group does: the form's, then a
        ``Choice`` around it in the group.

        Args:
            choices: The form's statement.

        Returns:
            The classes for size, colour and variant, in that order, for each
            one that resolves to a class.

        Raises:
            InvalidChoice: A size, colour or variant stated is not one daisyUI
                has for an input, or the ``Choice`` around the text states a
                drawing or a label, which text has none of.
        """
        own = Choice() if self.choice is None else self.choice
        for kind in ("drawing", "label"):
            stated = getattr(own, kind)
            if stated is not None and stated is not INHERIT:
                raise InvalidChoice(kind, stated, ())
        resolved = (
            Modifiers.resolve(
                kind,
                self.component,
                own=getattr(own, kind),
                form=getattr(choices, kind),
            )
            for kind in ("size", "color", "variant")
        )
        return [modifier for modifier in resolved if modifier]


class Join(LayoutObject):
    """Fields, text and buttons drawn as one daisyUI join under one label.

    A group of several fields is a fieldset whose legend is the label. A group
    of one field is drawn as that field is anywhere else: a label for its input,
    which is the group's label or else the field's own, the join, and the
    field's help text and errors. Text before or after one input, such as
    ``Join("price", HTML("$"))``, is a group of one field. Each member is an input
    or a select, named for assistive technology by its own label, and keeps its
    own help text and errors. A hidden member is drawn beside the join, not in
    it. A ``Field`` holds the names it gives attributes to, and a ``Choice`` the
    names and buttons it states a size, colour or variant for. A button is drawn
    in its place in the join, as it is drawn anywhere else, with ``join-item``
    added. ``HTML`` is text between the inputs, such as a ``±`` between a value
    and its uncertainty, drawn in its place in the join, framed and sized as an
    input. Nothing else is held, and a ``Field`` with a ``wrapper_class`` or a
    ``template`` of its own is refused, because a member has no frame for either
    to apply to.

    ``FieldInput``'s ``member`` and ``is_member`` are about this. Its ``join``
    option and ``is_joined`` property are about django-crispy-forms'
    ``FieldWithButtons``, which this replaces.

    Args:
        *fields: The field names, ``Field`` objects, ``Choice`` objects,
            buttons and ``HTML`` that make up the group, in the order they are
            drawn.
        label: The group's one label, as text. A group of several fields
            without one has no legend, and a group of one field without one
            takes the field's label.
        css_id: The id of the element that carries ``join``.
        css_class: Classes for the element that carries ``join``.
        **attrs: Attributes for the element that carries ``join``. Underscores
            in a name become hyphens.
    """

    template = "%s/layout/join.html"
    member_template = "%s/layout/join_member.html"
    # Placed in the context while a button of the group is drawn.
    context_name = "daisyui_join"

    def __init__(
        self,
        *fields: Any,
        label: str | None = None,
        css_id: str | None = None,
        css_class: str | None = None,
        **attrs: Any,
    ) -> None:
        self.fields = list(fields)
        self.label = label
        self.css_id = css_id
        self.css_class = css_class
        self.flat_attrs = flatatt(attrs)

    @property
    def label_text(self) -> str:
        """The label as plain text, for an attribute that is escaped once.

        A label marked safe is markup, so its tags are dropped and its entities
        read as characters. Any other label is returned as written, and no label
        is an empty string.
        """
        if self.label is None:
            return ""
        # A lazy label says whether it is safe only once it is read.
        plain = str(self.label)
        if isinstance(plain, SafeData):
            return unescape(strip_tags(plain)).strip()
        return plain

    def members(self) -> list[Member]:
        """Return the fields the group holds, in the order it holds them.

        Returns:
            One entry for each field name: a name on its own, each name of a
            ``Field`` with that ``Field``'s attributes, and each name a
            ``Choice`` holds with the ``Choice`` merged over any ``Choice``
            further out in the group.

        Raises:
            InvalidMember: See ``contents``.
        """
        return [entry for entry in self.contents() if isinstance(entry, Member)]

    def contents(self) -> list[Member | GroupButton | GroupText]:
        """Return the fields, the buttons and the text the group holds, in order.

        Returns:
            The members, as ``members`` gives them, one ``GroupButton`` for
            each button and one ``GroupText`` for each ``HTML``, in the order
            the group holds them.

        Raises:
            InvalidMember: The group holds a layout object other than ``Field``,
                ``Choice``, a button and ``HTML``, which includes a subclass of ``Field``
                and a ``Hidden``, or a ``Field`` with a ``wrapper_class`` or a
                ``template`` of its own, which a member has no frame for.
        """
        return self.contents_of(self.fields, None)

    def contents_of(
        self, held: list[Any], outer: Choice | None
    ) -> list[Member | GroupButton | GroupText]:
        """Return the contents of one level of the group.

        Args:
            held: What a ``Join`` or a ``Choice`` in it holds.
            outer: The merged ``Choice`` around ``held``, or None.

        Returns:
            The contents, in order.

        Raises:
            InvalidMember: See ``contents``.
        """
        found: list[Member | GroupButton | GroupText] = []
        for item in held:
            if isinstance(item, str):
                found.append(Member(item, {}, outer))
            elif GroupButton.accepts(item):
                found.append(GroupButton(item, outer))
            elif type(item) is HTML:
                found.append(GroupText(item, outer))
            elif type(item) is Field:
                if item.wrapper_class or item.template != Field.template:
                    raise InvalidMember(type(item).__name__)
                found.extend(
                    Member(name, dict(item.attrs), outer) for name in item.fields
                )
            elif isinstance(item, Choice):
                placed = item.over(outer if outer is not None else Choice())
                found.extend(self.contents_of(item.fields, placed))
            else:
                raise InvalidMember(type(item).__name__)
        return found

    def draw(
        self,
        entry: Member | GroupButton | GroupText,
        form: Any,
        context: Context,
        template_pack: str,
        lone: bool = False,
    ) -> SafeString:
        """Draw one entry through django-crispy-forms.

        For a member, a ``Field`` made for it, with the member template and the
        attributes it was given, is rendered by ``render_field``.
        django-crispy-forms marks the field as rendered, applies the attributes
        and deals with a name the form lacks. A button is rendered by
        ``render_field`` as it is anywhere else, with the group placed in the
        context so that it is drawn as an item of the join. Either is drawn
        inside the entry's ``Choice`` when it has one. Text is drawn by its
        ``HTML`` with the form's context, inside an element that is an item of
        the join and takes the size, colour and variant an input would.

        Args:
            entry: The member, the button or the text to draw.
            form: The form being drawn.
            context: The template context.
            template_pack: The template pack drawing the layout.
            lone: Whether the entry is the group's one field, which the group's
                label names, unless the developer wrote an ``aria-label``.

        Returns:
            The entry's markup, empty for a name the form lacks.

        Raises:
            InvalidChoice: See ``GroupText.classes``.
        """
        if isinstance(entry, GroupText):
            choices = FormChoices.lookup(context, form) or FormChoices()
            return SafeString(
                render_to_string(
                    entry.template % template_pack,
                    {
                        "text": entry.text.render(
                            form, context, template_pack=template_pack
                        ),
                        "classes": " ".join(entry.classes(choices)),
                    },
                )
            )
        held: Any = (
            entry.button
            if isinstance(entry, GroupButton)
            else entry.field(self.member_template % template_pack)
        )
        if (
            lone
            and self.label is not None
            and isinstance(entry, Member)
            and "aria-label" not in form.fields[entry.name].widget.attrs
        ):
            held.attrs.setdefault("aria-label", self.label_text)
        if entry.choice is not None:
            chosen = entry.choice.over(Choice())
            chosen.fields = [held]
            held = chosen
        layer = {self.context_name: self} if isinstance(entry, GroupButton) else {}
        with Choice.placed_in(context, layer):
            drawn: SafeString = render_field(
                held, form, context, template_pack=template_pack
            )
        return drawn

    def render(
        self,
        form: Any,
        context: Context,
        template_pack: str = TEMPLATE_PACK,
        **kwargs: Any,
    ) -> SafeString:
        """Draw the group.

        A group of one visible field is drawn in that field's frame, under a
        label for its input. A hidden member is drawn beside the join, because daisyUI squares the
        first and last child of the element that carries ``join``, whatever
        they are. Whether a member is hidden is read after it is drawn, because
        ``Field("name", type="hidden")`` makes it so while it is drawn. A name
        the form lacks is neither a visible nor a hidden member. A button and
        text are drawn in the join in their place. Text has nothing to stand
        between without a visible member or a button, so it alone draws no join.

        Args:
            form: The form being drawn.
            context: The template context.
            template_pack: The template pack drawing the layout.
            **kwargs: Not used. django-crispy-forms passes them to every layout
                object.

        Returns:
            The group's markup. Nothing for a group that holds nothing, and
            only the hidden inputs for a group with no visible member and no
            button.

        Raises:
            InvalidMember: See ``contents``.
            InvalidChoice: A choice the group states is not one daisyUI has.
        """
        inputs: list[str] = []
        hidden: list[str] = []
        shown: list[Any] = []
        has_control = False
        contents = self.contents()
        visible = [
            entry
            for entry in contents
            if isinstance(entry, Member)
            and entry.name in form.fields
            and not form[entry.name].is_hidden
            and entry.attrs.get("type") != "hidden"
        ]
        lone = visible[0] if len(visible) == 1 else None
        for entry in contents:
            drawn = self.draw(entry, form, context, template_pack, entry is lone)
            if isinstance(entry, GroupText):
                inputs.append(drawn)
                continue
            if isinstance(entry, GroupButton):
                inputs.append(drawn)
                has_control = True
                continue
            if entry.name not in form.fields:
                continue
            bound = form[entry.name]
            if bound.is_hidden:
                hidden.append(drawn)
            else:
                inputs.append(drawn)
                shown.append(bound)
                has_control = True
        if not has_control:
            return SafeString("".join(hidden))
        required = next((bound for bound in shown if bound.field.required), None)
        markup: SafeString = SafeString(
            render_to_string(
                self.get_template_name(template_pack),
                {
                    **cast(dict[str, Any], context.flatten()),
                    "join": self,
                    "inputs": SafeString("".join(inputs)),
                    "hidden": SafeString("".join(hidden)),
                    "members": shown,
                    "lone": shown[0] if len(shown) == 1 else None,
                    "required": required,
                },
            )
        )
        return markup


class Fieldset(CrispyFieldset):
    """A fieldset drawn as a panel, which can carry a description and collapse.

    Everything django-crispy-forms' own ``Fieldset`` takes is taken here and kept
    as it is. A collapsible fieldset is opened and closed by its legend, and one
    holding a field in error is drawn open whatever its state.

    Args:
        legend: The fieldset's legend, rendered as a template against the page's
            context.
        *fields: The fields and layout objects it holds.
        collapsible: Whether a person can open and close it.
        state: ``"open"`` or ``"closed"``, how a collapsible fieldset is first
            drawn. A collapsible fieldset with no state is drawn closed.
        description: Help text drawn at the top of the fieldset, before its
            first field, and read out with the fieldset's name.
        **kwargs: Passed to django-crispy-forms' ``Fieldset``.

    Raises:
        ValueError: The state is not ``"open"`` or ``"closed"``, a state is given
            for a fieldset that is not collapsible, or a collapsible fieldset has
            no legend to open it by.
    """

    states = ("open", "closed")

    def __init__(
        self,
        legend: str,
        *fields: Any,
        collapsible: bool = False,
        state: str | None = None,
        description: str = "",
        **kwargs: Any,
    ) -> None:
        if state is not None and state not in self.states:
            raise ValueError(
                f"{state!r} is not a fieldset state: use 'open' or 'closed'"
            )
        if state is not None and not collapsible:
            raise ValueError("A fieldset has a state only when it is collapsible")
        if collapsible and not legend:
            raise ValueError("A collapsible fieldset needs a legend to open it by")
        super().__init__(legend, *fields, **kwargs)
        self.collapsible = collapsible
        self.state = state or "closed"
        self.description = description

    def render(
        self,
        form: Any,
        context: Context,
        template_pack: str = TEMPLATE_PACK,
        **kwargs: Any,
    ) -> SafeString:
        """Draw the fieldset, open when it holds a field in error.

        The ids the template writes start with the fieldset's ``css_id``, or
        with its legend made into a slug, and with the form's prefix, so the
        forms of a formset do not share them.
        """
        fields = self.get_rendered_fields(form, context, template_pack, **kwargs)
        legend = Template(str(self.legend)).render(context) if self.legend else ""
        in_error = any(
            pointer.name in form.errors for pointer in self.get_field_names()
        )
        name = self.css_id or slugify(strip_tags(legend) or self.description)
        prefix = f"{form.prefix}-" if form.prefix else ""
        context.update(
            {
                "fieldset": self,
                "legend": SafeString(legend),
                "fields": fields,
                "fieldset_id": f"{prefix}{name or 'fieldset'}",
                "fieldset_in_error": in_error,
                "fieldset_open": self.state == "open" or in_error,
            }
        )
        template = self.get_template_name(template_pack)
        return render_to_string(template, cast(dict[str, Any], context.flatten()))
