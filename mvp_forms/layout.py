"""Layout objects the package defines, beside those of django-crispy-forms."""

from dataclasses import dataclass
from html import unescape
from typing import Any, cast

from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import BaseInput, Field, LayoutObject
from crispy_forms.utils import TEMPLATE_PACK, flatatt, render_field
from django.template import Context
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import SafeData, SafeString

from mvp_forms.choices import Choice


class InvalidMember(ValueError):
    """Something in a joined group that cannot be joined.

    Args:
        member: The name of the field, when its widget is not an input or a
            select, or the class name of the layout object, when the group holds
            anything but field names, ``Field``, ``Choice`` and buttons.
    """

    def __init__(self, member: str) -> None:
        self.member = member
        super().__init__(
            f"{member!r} cannot be a member of a joined group: only a field drawn "
            "as an input or a select can, named alone, in a Field or in a Choice, "
            "and a button"
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


class Join(LayoutObject):
    """Several fields drawn as one daisyUI join under one label.

    The group is a fieldset whose legend is the label. Each member is an input
    or a select, named for assistive technology by its own label, and keeps its
    own help text and errors. A hidden member is drawn beside the join, not in
    it. A ``Field`` holds the names it gives attributes to, and a ``Choice`` the
    names and buttons it states a size, colour or variant for. A button is drawn
    in its place in the join, as it is drawn anywhere else, with ``join-item``
    added. Nothing else is held, and a ``Field`` with a ``wrapper_class`` or a
    ``template`` of its own is refused, because a member has no frame for either
    to apply to.

    This is the group of several fields. ``FieldWithButtons`` is the one field
    that has buttons joined to it, and ``FieldInput``'s ``join`` option and
    ``is_joined`` property are about that, while ``member`` and ``is_member``
    are about this.

    Args:
        *fields: The field names, ``Field`` objects, ``Choice`` objects and
            buttons that make up the group, in the order they are drawn.
        label: The group's one label, as text. A group without one has no
            legend.
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

    def contents(self) -> list[Member | GroupButton]:
        """Return the fields and the buttons the group holds, in order.

        Returns:
            The members, as ``members`` gives them, and one ``GroupButton`` for
            each button, in the order the group holds them.

        Raises:
            InvalidMember: The group holds a layout object other than ``Field``,
                ``Choice`` and a button, which includes a subclass of ``Field``
                and a ``Hidden``, or a ``Field`` with a ``wrapper_class`` or a
                ``template`` of its own, which a member has no frame for.
        """
        return self.contents_of(self.fields, None)

    def contents_of(
        self, held: list[Any], outer: Choice | None
    ) -> list[Member | GroupButton]:
        """Return the contents of one level of the group.

        Args:
            held: What a ``Join`` or a ``Choice`` in it holds.
            outer: The merged ``Choice`` around ``held``, or None.

        Returns:
            The contents, in order.

        Raises:
            InvalidMember: See ``contents``.
        """
        found: list[Member | GroupButton] = []
        for item in held:
            if isinstance(item, str):
                found.append(Member(item, {}, outer))
            elif GroupButton.accepts(item):
                found.append(GroupButton(item, outer))
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
        entry: Member | GroupButton,
        form: Any,
        context: Context,
        template_pack: str,
    ) -> SafeString:
        """Draw one entry through django-crispy-forms.

        For a member, a ``Field`` made for it, with the member template and the
        attributes it was given, is rendered by ``render_field``.
        django-crispy-forms marks the field as rendered, applies the attributes
        and deals with a name the form lacks. A button is rendered by
        ``render_field`` as it is anywhere else, with the group placed in the
        context so that it is drawn as an item of the join. Either is drawn
        inside the entry's ``Choice`` when it has one.

        Args:
            entry: The member or the button to draw.
            form: The form being drawn.
            context: The template context.
            template_pack: The template pack drawing the layout.

        Returns:
            The entry's markup, empty for a name the form lacks.
        """
        held: Any = (
            entry.button
            if isinstance(entry, GroupButton)
            else entry.field(self.member_template % template_pack)
        )
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

        A hidden member is drawn beside the join, because daisyUI squares the
        first and last child of the element that carries ``join``, whatever
        they are. Whether a member is hidden is read after it is drawn, because
        ``Field("name", type="hidden")`` makes it so while it is drawn. A name
        the form lacks is neither a visible nor a hidden member. A button is
        drawn in the join in its place.

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
        for entry in self.contents():
            drawn = self.draw(entry, form, context, template_pack)
            if isinstance(entry, GroupButton):
                inputs.append(drawn)
                continue
            if entry.name not in form.fields:
                continue
            bound = form[entry.name]
            if bound.is_hidden:
                hidden.append(drawn)
            else:
                inputs.append(drawn)
                shown.append(bound)
        if not inputs:
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
                    "required": required,
                },
            )
        )
        return markup
