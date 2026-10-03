"""The frame drawn around each field: label, marker, help text and errors."""

import pytest
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.utils.safestring import mark_safe


class RequirementForm(forms.Form):
    name = forms.CharField(label="Name")
    nickname = forms.CharField(label="Nickname", required=False)


class NoRequiredAttributeForm(RequirementForm):
    use_required_attribute = False


class UnlabelledForm(forms.Form):
    name = forms.CharField(label="")


class DescriptionForm(forms.Form):
    neither = forms.CharField(required=False)
    helped = forms.CharField(required=False, help_text="Some help")
    failing = forms.CharField()
    both = forms.CharField(help_text="Some help")


DESCRIBED_BY = [
    ("neither", set()),
    ("helped", {"helptext"}),
    ("failing", {"error"}),
    ("both", {"helptext", "error"}),
]


def reject_markup(value):
    raise ValidationError("<script>alert(1)</script>", code="markup")


class UnsafeForm(forms.Form):
    name = forms.CharField(
        label="<b>Name</b>", help_text="<i>Help</i>", validators=[reject_markup]
    )


class SafeHelpForm(forms.Form):
    name = forms.CharField(help_text=mark_safe("<em>Help</em>"))


class SeveralErrorsForm(forms.Form):
    code = forms.CharField(
        validators=[MinLengthValidator(5), MinLengthValidator(8)],
    )


class PrefixedForm(forms.Form):
    name = forms.CharField(help_text="Some help")


class TestLabel:
    def test_the_label_is_tied_to_the_input_it_names(self, draw):
        soup = draw("{{ form|crispy }}", form=RequirementForm())

        label = soup.find("label")

        assert label["for"] == soup.find("input")["id"]

    def test_an_empty_label_leaves_no_label_element(self, draw):
        soup = draw("{{ form|crispy }}", form=UnlabelledForm())

        assert soup.find("label") is None
        assert soup.find(id="id_name") is not None


class TestRequiredMarker:
    def test_a_required_field_has_a_marker_hidden_from_assistive_technology(self, draw):
        soup = draw("{{ form|crispy }}", form=RequirementForm())

        label = soup.find("label", attrs={"for": "id_name"})

        assert label.find(attrs={"aria-hidden": "true"}) is not None

    def test_an_optional_field_has_no_marker(self, draw):
        soup = draw("{{ form|crispy }}", form=RequirementForm())

        label = soup.find("label", attrs={"for": "id_nickname"})

        assert label.find(attrs={"aria-hidden": "true"}) is None

    def test_a_required_input_carries_the_required_attribute(self, draw):
        soup = draw("{{ form|crispy }}", form=RequirementForm())

        assert soup.find(id="id_name").has_attr("required")
        assert not soup.find(id="id_nickname").has_attr("required")

    def test_a_form_without_the_required_attribute_still_has_the_marker(self, draw):
        soup = draw("{{ form|crispy }}", form=NoRequiredAttributeForm())

        label = soup.find("label", attrs={"for": "id_name"})

        assert label.find(attrs={"aria-hidden": "true"}) is not None

    def test_a_form_without_the_required_attribute_marks_the_input_aria_required(
        self, draw
    ):
        soup = draw("{{ form|crispy }}", form=NoRequiredAttributeForm())

        required, optional = soup.find(id="id_name"), soup.find(id="id_nickname")

        assert not required.has_attr("required")
        assert required["aria-required"] == "true"
        assert not optional.has_attr("aria-required")


class TestDescription:
    @pytest.mark.parametrize(("name", "parts"), DESCRIBED_BY)
    def test_the_input_describes_itself_by_exactly_what_is_drawn(
        self, draw, name, parts
    ):
        soup = draw("{{ form|crispy }}", form=DescriptionForm({}))

        frame = soup.find(id=f"div_id_{name}")
        described = set(frame.find("input").get("aria-describedby", "").split())

        assert described == {f"id_{name}_{part}" for part in parts}
        drawn = {t["id"] for t in frame.find_all(id=True)}
        drawn -= {f"div_id_{name}", f"id_{name}"}
        assert drawn == described

    @pytest.mark.parametrize(("name", "parts"), DESCRIBED_BY)
    def test_every_id_an_input_describes_itself_by_is_on_the_page(
        self, draw, name, parts
    ):
        soup = draw("{{ form|crispy }}", form=DescriptionForm({}))

        described = soup.find(id=f"id_{name}").get("aria-describedby", "").split()

        assert all(soup.find(id=referenced) is not None for referenced in described)


class TestErrors:
    def test_an_invalid_input_is_marked_invalid_and_drawn_in_the_error_state(
        self, draw
    ):
        soup = draw("{{ form|crispy }}", form=DescriptionForm({}))

        failing, valid = soup.find(id="id_failing"), soup.find(id="id_helped")

        assert failing["aria-invalid"] == "true"
        assert "input-error" in failing["class"]
        assert not valid.has_attr("aria-invalid")
        assert "input-error" not in valid["class"]

    def test_every_message_is_inside_the_one_error_element(self, draw):
        form = SeveralErrorsForm({"code": "abc"})

        soup = draw("{{ form|crispy }}", form=form)

        assert len(soup.find_all(id="id_code_error")) == 1
        drawn = [p.get_text(strip=True) for p in soup.find(id="id_code_error")("p")]
        assert drawn == list(form["code"].errors)
        assert len(drawn) == 2


class TestEscaping:
    def test_markup_in_a_label_help_text_or_error_is_escaped(self, draw):
        soup = draw("{{ form|crispy }}", form=UnsafeForm({"name": "x"}))

        frame = soup.find(id="div_id_name")

        assert frame.find("label").find("b") is None
        assert "<b>Name</b>" in frame.find("label").get_text()
        assert frame.find(id="id_name_helptext").find("i") is None
        assert frame.find(id="id_name_error").find("script") is None
        assert "<script>" in frame.find(id="id_name_error").get_text()

    def test_help_text_marked_safe_keeps_its_markup(self, draw):
        soup = draw("{{ form|crispy }}", form=SafeHelpForm())

        assert soup.find(id="id_name_helptext").find("em") is not None


class TestPrefixes:
    def test_two_prefixed_forms_share_no_id_and_each_resolves_inside_itself(self, draw):
        one = PrefixedForm(prefix="one", data={})
        two = PrefixedForm(prefix="two", data={})

        soup = draw(
            '<section id="one">{{ one|crispy }}</section>'
            '<section id="two">{{ two|crispy }}</section>',
            one=one,
            two=two,
        )

        ids = [tag["id"] for tag in soup.find_all(id=True)]
        assert len(ids) == len(set(ids))
        for section in (soup.find(id="one"), soup.find(id="two")):
            references = [label["for"] for label in section("label")]
            for described in section("input"):
                references += described["aria-describedby"].split()
            assert references
            assert all(section.find(id=ref) is not None for ref in references)


class TestIdsTurnedOff:
    def test_a_form_without_ids_emits_no_id_no_for_and_no_description(self, draw):
        form = DescriptionForm({}, auto_id=False)

        soup = draw("{{ form|crispy }}", form=form)

        assert soup.find_all(id=True) == []
        assert all(not label.has_attr("for") for label in soup("label"))
        assert all(not tag.has_attr("aria-describedby") for tag in soup("input"))
