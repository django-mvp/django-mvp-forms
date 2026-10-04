"""Text the pack draws with daisyUI's `label` class wraps on a narrow page."""

from tests.legibility.catalogue import Catalogue

WRAPS = "text-wrap"
ATTACHED_TO = {"input", "select"}


def labels():
    """Every element drawn with daisyUI's `label` class, with its state's name."""
    return [
        (state.name, tag)
        for state in Catalogue.states()
        for tag in state.soup.find_all(class_="label")
    ]


def is_attached(tag):
    return bool(ATTACHED_TO & set(tag.parent.get("class", [])))


def kind(tag):
    control = tag.find("input")
    return tag.name, control["type"] if control else None


class TestLabelsWrap:
    def test_every_label_outside_an_input_wraps(self):
        free = [(name, tag) for name, tag in labels() if not is_attached(tag)]

        kept_on_one_line = sorted(
            {(name, *kind(tag)) for name, tag in free if WRAPS not in tag["class"]}
        )

        assert {("p", None), ("label", "radio"), ("label", "checkbox")} <= {
            kind(tag) for _, tag in free
        }
        assert any(tag.find("input", attrs={"name": "held-clear"}) for _, tag in free)
        assert kept_on_one_line == []

    def test_text_attached_to_an_input_is_left_on_one_line(self):
        attached = [tag for _, tag in labels() if is_attached(tag)]

        assert attached
        assert [tag for tag in attached if WRAPS in tag["class"]] == []
