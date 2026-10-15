# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/035f3fbd2b81479a.md
# this_file: ports/dialogs/pyqt-official/classwizard-035f3fbd2b81479a.py

import importlib.util
import sys
from pathlib import Path

_key = "fontlab_cleanroom_a_primitives"
if _key not in sys.modules:
    _path = (
        Path(__file__).resolve().parents[2]
        / "layouts/pyqt-official/basiclayouts-2f94fe07de765888.py"
    )
    _spec = importlib.util.spec_from_file_location(_key, _path)
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_key] = _module
    try:
        _spec.loader.exec_module(_module)
    except BaseException:
        sys.modules.pop(_key, None)
        raise
S = sys.modules[_key]

import re


def skeleton(name, base, style, copy, macro, guard, include, header):
    if not re.fullmatch(r"[A-Za-z_]\w*", name) or (
        base and not re.fullmatch(r"[A-Za-z_]\w*(?:::\w+)*", base)
    ):
        raise ValueError("Use C++ identifiers for Name and Base")
    guard_name = name.upper() + "_H"
    prefix = (
        f"#ifndef {guard_name}\n#define {guard_name}\n" if guard else "#pragma once\n"
    )
    if include and base:
        prefix += f"#include <{base}>\n"
    inheritance = " : public " + base if base else ""
    signature = (
        f"{name}()"
        if style == 0
        else f"explicit {name}(QObject *parent = nullptr)"
        if style == 1
        else f"{name}(const {base or 'QObject'} &source)"
    )
    declaration = (
        prefix
        + f"\n// A small class ready for your own behavior.\nclass {name}{inheritance}\n{{\n"
    )
    if macro:
        declaration += "    Q_OBJECT\n"
    declaration += "public:\n    " + signature + ";\n"
    if copy:
        declaration += f"    {name}(const {name} &) = default;\n    {name} &operator=(const {name} &) = default;\n"
    declaration += "};\n" + ("\n#endif\n" if guard else "")
    implementation = (
        f'#include "{header}"\n\n'
        + name
        + "::"
        + signature.replace("explicit ", "").replace(" = nullptr", "")
    )
    if base and style == 1:
        implementation += " : " + base + "(parent)"
    if base and style == 2:
        implementation += " : " + base + "(source)"
    implementation += "\n{\n    // Add initialization here.\n}\n"
    return declaration, implementation


def build(qt):
    state = {}

    class Wizard(qt.QtGui.QWizard):
        def validateCurrentPage(self):
            if int(S.value(self, "currentId")) != 4:
                return True
            return state["write"]()

    with S.Session(qt, "C++ class skeleton", Wizard()) as s:
        s.window.setOption(s.g.QWizard.IndependentPages, True)
        pages = []
        for title in [
            "Introduction",
            "Class and base",
            "Formatting",
            "Output locations",
            "Review",
        ]:
            page = s.g.QWizardPage()
            page.setTitle(title)
            pages.append((page, s.vertical(page)))
            s.window.addPage(page)
        s.label(
            "Choose a class shape, review it, then create two source files.",
            pages[0][1],
        )
        name = s.line("name", layout=pages[1][1])
        base = s.line("base", layout=pages[1][1])
        pages[1][0].registerField("name*", name)
        style = s.combo(
            "constructor", ["Default", "QObject parent", "Base source"], pages[2][1]
        )
        copy = s.check("copy", "Copy operations", layout=pages[2][1])
        macro = s.check("macro", "Qt object macro", layout=pages[2][1])
        guard = s.check("guard", "Header guard", True, pages[2][1])
        inc = s.check("include", "Include base", True, pages[2][1])
        folder = s.line("folder", str(s.temp()), pages[3][1])
        header = s.line("header", "", pages[3][1])
        source = s.line("source", "", pages[3][1])
        for key, obj in [("folder", folder), ("header", header), ("source", source)]:
            pages[3][0].registerField(key + "*", obj)
        report = s.keep(
            "report", s.label("Review your settings before Finish.", pages[4][1])
        )

        def derived(*args):
            stem = str(S.value(name, "text")).lower()
            header.setText(stem + ".h" if stem else "")
            source.setText(stem + ".cpp" if stem else "")
            report.setText(
                "Class "
                + str(S.value(name, "text"))
                + " with base "
                + str(S.value(base, "text"))
            )

        s.link(name, "textChanged(QString)", derived)
        s.link(base, "textChanged(QString)", derived)

        def generate():
            try:
                hname = str(S.value(header, "text"))
                cname = str(S.value(source, "text"))
                if (
                    Path(hname).name != hname
                    or Path(cname).name != cname
                    or hname == cname
                ):
                    raise ValueError("Choose two distinct filenames")
                files = skeleton(
                    str(S.value(name, "text")),
                    str(S.value(base, "text")),
                    int(S.value(style, "currentIndex")),
                    bool(S.value(copy, "checked")),
                    bool(S.value(macro, "checked")),
                    bool(S.value(guard, "checked")),
                    bool(S.value(inc, "checked")),
                    hname,
                )
                root = Path(str(S.value(folder, "text")))
                # Exclusive creation protects an existing user's source files.
                made = []
                try:
                    for filename, text in zip([hname, cname], files):
                        with (root / filename).open("x", encoding="utf-8") as stream:
                            made.append(root / filename)
                            stream.write(text)
                except OSError:
                    for path in made:
                        path.unlink(missing_ok=True)
                    raise
                s.state["written"] = [hname, cname]
                s.state["error"] = ""
                return True
            except (OSError, ValueError) as error:
                s.state["error"] = str(error)
                report.setText(str(error))
                return False

        state["write"] = generate
        s.keep("generate", generate)
        for i, (page, layout) in enumerate(pages):
            for role, w, h in [
                (s.g.QWizard.BannerPixmap, 360, 60),
                (s.g.QWizard.WatermarkPixmap, 100, 300),
                (s.g.QWizard.LogoPixmap, 32, 32),
            ]:
                artwork = s.g.QPixmap(w, h)
                artwork.fill(s.g.QColor("#e9eff6"))
                painter = s.g.QPainter(artwork)
                try:
                    painter.setBrush(s.g.QColor("#446d99"))
                    painter.drawEllipse(4, 4, min(w, h) - 8, min(w, h) - 8)
                    painter.setPen(s.g.QColor("#33485f"))
                    painter.drawText(10, h - 12, str(i + 1) + " / 5")
                finally:
                    painter.end()
                page.setPixmap(role, artwork)
        s.link(s.window, "accepted()", lambda *a: s.h.close())
        s.link(s.window, "rejected()", lambda *a: s.h.close())
        return s.h
