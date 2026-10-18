# this_file: lessons/candidate_tests/models_candidate/test_domain.py
"""Exercise real-font source guards with immutable owned boundary doubles."""

from dataclasses import replace
from types import SimpleNamespace as NS

import pytest

from fontlab_python_lessons.domain import capture, ensure_current, filtered, preview


class Source:
    """Expose only the existing fly.ap.scripting read/selection boundary."""

    def __init__(self):
        self.package = NS(id=14, master="Regular")
        self.names = ["space", "A", "Aacute", "zero"]
        self.selected = ["zero", "A"]
        self.rows = {"space": (0, None), "A": (600, 0), "Aacute": (620, -12), "zero": (0, 0)}

    def current_package(self, expected_id=None):
        return (
            self.package
            if self.package is not None and expected_id in (None, self.package.id)
            else None
        )

    def names_font_glyphs(self):
        return [(name, []) for name in self.names]

    def names_font_window_selection(self):
        return self.selected

    def inspectors_api(self):
        def layout(package, names, master):
            assert package is self.package and master == package.master
            return [(n, 0, *self.rows[n], None) for n in names if n in self.rows]

        return NS(layout=layout)


def test_capture_metrics_when_zero_width_or_lsb_then_preserves_values_and_font_order():
    source = Source()
    actual = capture(source, "metrics")
    assert actual.selected == ("A", "zero"), "Selection must follow font order"
    assert [(r.name, r.advance, r.lsb) for r in actual.rows] == [("A", 600, 0), ("zero", 0, 0)]


def test_capture_form_when_missing_layer_then_retains_missing_row():
    source = Source()
    del source.rows["A"]
    actual = capture(source, "form", "A")
    assert actual.rows[0].advance is None and actual.rows[0].lsb is None


@pytest.mark.parametrize("change", ["font", "master", "names", "metrics", "selection"])
def test_ensure_current_when_source_changed_then_refuses(change):
    source = Source()
    scanned = capture(source, "metrics")
    if change == "font":
        source.package = NS(id=15, master="Regular")
    elif change == "master":
        source.package.master = "Bold"
    elif change == "names":
        source.names.append("new")
    elif change == "metrics":
        source.rows["A"] = (601, 0)
    else:
        source.selected = []
    with pytest.raises(ValueError, match="Refresh"):
        ensure_current(source, scanned)


def test_capture_when_no_font_or_no_glyphs_then_explicit_and_empty():
    source = Source()
    source.package = None
    with pytest.raises(ValueError, match="Open a font"):
        capture(source, "names")
    source.package = NS(id=1, master="Regular")
    source.names = source.selected = []
    assert capture(source, "form").rows == (), "Empty fonts must not invent glyphs"


def test_filter_when_case_or_empty_prefix_then_preserves_original_font_order():
    names = ("space", "A", "Aacute", "a.alt")
    assert filtered(names, "a") == ("A", "Aacute", "a.alt")
    assert filtered(names, "") == names
    assert filtered(names, "zz") == ()


def test_preview_when_hypothetical_then_returns_delta_without_modifying_source():
    source = Source()
    row = capture(source, "form", "zero").rows[0]
    assert (
        preview(row, 12.5) == "zero: actual 0; preview 12.5; change +12.5 font units. No font edit."
    )
    assert source.rows["zero"] == (0, 0), "Preview must never call a font setter"
    for value in [float("nan"), float("inf")]:
        with pytest.raises(ValueError, match="finite"):
            preview(row, value)
    with pytest.raises(ValueError, match="layer"):
        preview(replace(row, advance=None), 12)


def test_capture_when_unknown_mode_name_or_midread_master_change_then_refuses():
    source = Source()
    with pytest.raises(ValueError):
        capture(source, "other")
    with pytest.raises(ValueError, match="glyph"):
        capture(source, "form", "missing")
    source.names_font_window_selection = lambda: setattr(source.package, "master", "Bold") or []
    with pytest.raises(ValueError, match="Refresh"):
        capture(source, "metrics")
