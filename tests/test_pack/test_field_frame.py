"""The frame drawn around each field: label, marker, help text and errors."""

from django import forms


class RequirementForm(forms.Form):
    name = forms.CharField(label="Name")
    nickname = forms.CharField(label="Nickname", required=False)


class NoRequiredAttributeForm(RequirementForm):
    use_required_attribute = False


class UnlabelledForm(forms.Form):
    name = forms.CharField(label="")


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
