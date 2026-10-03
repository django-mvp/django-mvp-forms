"""The layout objects that group fields: containers, rows, columns and fieldsets."""

from crispy_forms.layout import Column, Div, Fieldset, Row

DEVELOPER_CLASSES = ["mine", "other"]
DEVELOPER_ATTRS = {"data-role": "group", "title": "Group"}
LEGEND = "Account"


def field_ids(container):
    return [tag["id"] for tag in container.find_all("input")]


class TestDiv:
    def test_it_holds_its_fields_in_layout_order(self, draw_layout):
        soup = draw_layout(Div("second", "first", css_id="box"))

        assert field_ids(soup.find("div", id="box")) == ["id_second", "id_first"]

    def test_it_draws_only_the_fields_the_layout_names(self, draw_layout):
        soup = draw_layout(Div("first", css_id="box"))

        assert soup.find(id="id_second") is None

    def test_it_carries_the_id_the_classes_and_the_attributes_it_was_given(
        self, draw_layout
    ):
        box = draw_layout(
            Div(
                "first",
                css_id="box",
                css_class=" ".join(DEVELOPER_CLASSES),
                **DEVELOPER_ATTRS,
            )
        ).find("div", id="box")

        assert box["class"] == DEVELOPER_CLASSES
        assert box["data-role"] == DEVELOPER_ATTRS["data-role"]
        assert box["title"] == DEVELOPER_ATTRS["title"]

    def test_it_writes_no_id_when_it_was_given_none(self, draw_layout):
        soup = draw_layout(Div("first", css_class="mine"))

        box = soup.find("div", class_="mine")
        assert not box.has_attr("id")

    def test_it_writes_no_class_attribute_when_it_was_given_none(self, draw_layout):
        soup = draw_layout(Div("first", css_id="box"))

        assert not soup.find("div", id="box").has_attr("class")

    def test_an_empty_one_is_drawn(self, draw_layout):
        soup = draw_layout(Div(css_id="box"))

        box = soup.find("div", id="box")
        assert box is not None
        assert box.find(["input", "div"]) is None

    def test_one_given_its_own_template_is_drawn_with_that_template(self, draw_layout):
        soup = draw_layout(
            Div("first", css_id="box", template="tests/own_container.html")
        )

        assert field_ids(soup.find("section", id="own-container")) == ["id_first"]
        assert soup.find("div", id="box") is None


class TestFieldset:
    def test_it_holds_its_fields_in_one_fieldset_in_layout_order(self, draw_layout):
        soup = draw_layout(Fieldset(LEGEND, "second", "first", css_id="group"))

        fieldsets = soup.find_all("fieldset", id="group")
        assert len(fieldsets) == 1
        assert field_ids(fieldsets[0]) == ["id_second", "id_first"]

    def test_its_legend_is_the_one_it_was_given(self, draw_layout):
        soup = draw_layout(Fieldset(LEGEND, "first", css_id="group"))

        legend = soup.find("fieldset", id="group").find("legend")
        assert legend.get_text(strip=True) == LEGEND

    def test_it_is_a_daisyui_fieldset_with_a_daisyui_legend(self, draw_layout):
        soup = draw_layout(Fieldset(LEGEND, "first", css_id="group"))

        fieldset = soup.find("fieldset", id="group")
        assert "fieldset" in fieldset["class"]
        assert "fieldset-legend" in fieldset.find("legend")["class"]

    def test_an_empty_legend_draws_no_legend_element(self, draw_layout):
        soup = draw_layout(Fieldset("", "first", css_id="group"))

        fieldset = soup.find("fieldset", id="group")
        assert fieldset.find("legend") is None
        assert field_ids(fieldset) == ["id_first"]

    def test_a_legend_reading_a_context_value_shows_it(self, draw_layout):
        soup = draw_layout(
            Fieldset("Data for {{ owner }}", "first", css_id="group"), owner="Ann"
        )

        legend = soup.find("fieldset", id="group").find("legend")
        assert "Ann" in legend.get_text()

    def test_markup_in_a_context_value_in_the_legend_is_escaped(self, draw_layout):
        soup = draw_layout(
            Fieldset("Data for {{ owner }}", "first", css_id="group"),
            owner="<b>Ann</b>",
        )

        legend = soup.find("fieldset", id="group").find("legend")
        assert legend.find("b") is None
        assert "<b>Ann</b>" in legend.get_text()

    def test_it_carries_the_id_the_classes_and_the_attributes_it_was_given(
        self, draw_layout
    ):
        fieldset = draw_layout(
            Fieldset(
                LEGEND,
                "first",
                css_id="group",
                css_class=" ".join(DEVELOPER_CLASSES),
                **DEVELOPER_ATTRS,
            )
        ).find("fieldset", id="group")

        assert set(DEVELOPER_CLASSES) <= set(fieldset["class"])
        assert "fieldset" in fieldset["class"]
        assert fieldset["data-role"] == DEVELOPER_ATTRS["data-role"]
        assert fieldset["title"] == DEVELOPER_ATTRS["title"]

    def test_an_empty_one_is_drawn(self, draw_layout):
        soup = draw_layout(Fieldset(LEGEND, css_id="group"))

        fieldset = soup.find("fieldset", id="group")
        assert fieldset is not None
        assert fieldset.find("input") is None

    def test_one_given_its_own_template_is_drawn_with_that_template(self, draw_layout):
        soup = draw_layout(
            Fieldset(
                LEGEND, "first", css_id="group", template="tests/own_container.html"
            )
        )

        assert field_ids(soup.find("section", id="own-container")) == ["id_first"]
        assert soup.find("fieldset", id="group") is None


class TestRowAndColumn:
    def test_each_field_is_in_its_own_column_inside_the_row_in_layout_order(
        self, draw_layout
    ):
        soup = draw_layout(
            Row(
                Column("second", css_id="left"),
                Column("first", css_id="right"),
                css_id="line",
            )
        )

        row = soup.find("div", id="line")
        columns = row.find_all("div", id=["left", "right"])
        assert [column["id"] for column in columns] == ["left", "right"]
        assert field_ids(columns[0]) == ["id_second"]
        assert field_ids(columns[1]) == ["id_first"]

    def test_a_row_carries_the_id_the_classes_and_the_attributes_it_was_given(
        self, draw_layout
    ):
        row = draw_layout(
            Row(
                "first",
                css_id="line",
                css_class=" ".join(DEVELOPER_CLASSES),
                **DEVELOPER_ATTRS,
            )
        ).find("div", id="line")

        assert set(DEVELOPER_CLASSES) < set(row["class"])
        assert row["data-role"] == DEVELOPER_ATTRS["data-role"]
        assert row["title"] == DEVELOPER_ATTRS["title"]

    def test_a_column_carries_the_id_the_classes_and_the_attributes_it_was_given(
        self, draw_layout
    ):
        column = draw_layout(
            Row(
                Column(
                    "first",
                    css_id="left",
                    css_class=" ".join(DEVELOPER_CLASSES),
                    **DEVELOPER_ATTRS,
                )
            )
        ).find("div", id="left")

        assert set(DEVELOPER_CLASSES) < set(column["class"])
        assert column["data-role"] == DEVELOPER_ATTRS["data-role"]
        assert column["title"] == DEVELOPER_ATTRS["title"]

    def test_a_row_and_a_column_write_no_id_when_given_none(self, draw_layout):
        soup = draw_layout(Row(Column("first", css_class="mine"), css_class="line"))

        assert not soup.find("div", class_="line").has_attr("id")
        assert not soup.find("div", class_="mine").has_attr("id")

    def test_a_column_outside_a_row_draws_its_fields(self, draw_layout):
        soup = draw_layout(Column("second", "first", css_id="left"))

        assert field_ids(soup.find("div", id="left")) == ["id_second", "id_first"]

    def test_a_row_holding_fields_directly_draws_them_in_order(self, draw_layout):
        soup = draw_layout(Row("second", "first", css_id="line"))

        assert field_ids(soup.find("div", id="line")) == ["id_second", "id_first"]

    def test_an_empty_row_and_an_empty_column_are_drawn(self, draw_layout):
        soup = draw_layout(Row(Column(css_id="left"), css_id="line"))

        assert soup.find("div", id="line").find("div", id="left") is not None


class TestNesting:
    def test_every_field_is_drawn_once_inside_the_containers_nested_as_laid_out(
        self, draw_layout
    ):
        soup = draw_layout(
            Div(
                Fieldset(
                    LEGEND,
                    Row(
                        Column("first", css_id="left"),
                        Column("second", "third", css_id="right"),
                        css_id="line",
                    ),
                    css_id="group",
                ),
                "fourth",
                css_id="box",
            )
        )

        for name in ["first", "second", "third", "fourth"]:
            assert len(soup.find_all(id=f"id_{name}")) == 1
        first = soup.find(id="id_first")
        column = first.find_parent("div", id="left")
        row = column.find_parent("div", id="line")
        fieldset = row.find_parent("fieldset", id="group")
        assert fieldset.find_parent("div", id="box") is not None
        assert soup.find(id="id_third").find_parent("div", id="right") is not None
        assert soup.find(id="id_fourth").find_parent("fieldset") is None

    def test_an_error_inside_nested_containers_is_drawn_in_its_own_frame(
        self, draw_layout
    ):
        soup = draw_layout(
            Row(
                Column(Fieldset(LEGEND, "first", css_id="group"), css_id="left"),
                css_id="line",
            ),
            bound=True,
        )

        error = soup.find(id="id_first_error")
        frame = soup.find(id="div_id_first")
        assert error.find_parent(id="div_id_first") is frame
        assert frame.find_parent("fieldset", id="group") is not None
        assert frame.find_parent("div", id="left") is not None

    def test_the_input_in_nested_containers_names_its_error(self, draw_layout):
        soup = draw_layout(
            Row(Column(Fieldset(LEGEND, "first", css_id="group"))), bound=True
        )

        described = soup.find(id="id_first")["aria-describedby"].split()
        assert "id_first_error" in described
