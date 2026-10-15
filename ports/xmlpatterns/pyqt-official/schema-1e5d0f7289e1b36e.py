# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/1e5d0f7289e1b36e.md
# this_file: ports/xmlpatterns/pyqt-official/schema-1e5d0f7289e1b36e.py

from contextlib import contextmanager

from fontlab_python_examples.handle import ExampleHandle


def value(obj, name):
    item = getattr(obj, name)
    return item() if callable(item) else item


@contextmanager
def owned(qt, title):
    state = {"closing": False}

    class Window(qt.QtGui.QWidget):
        def closeEvent(self, event):
            if not state["closing"]:
                handle.close()
            event.accept()

    window = Window()
    handle = ExampleHandle(window, dict)
    handle.cleanup.append(lambda: state.update(closing=True))
    try:
        window.setWindowTitle(title)
        window.setAttribute(qt.QtCore.Qt.WA_QuitOnClose, False)
        window.resize(760, 540)
        layout = qt.QtGui.QVBoxLayout(window)
        handle.controls["layout"] = layout
        yield handle, layout
    except BaseException:
        handle.close()
        raise


def wire(handle, obj, signature, callback):
    def receive(*args):
        if not handle.owner.closed:
            callback(*args)

    handle.connect_old(obj, signature, receive)
    return receive


def button(qt, handle, layout, name, callback):
    item = qt.QtGui.QPushButton(name, handle.widget)
    layout.addWidget(item)
    handle.controls[name] = item
    wire(handle, item, "clicked()", lambda *args: callback())
    return item


import re
import xml.etree.ElementTree as ET

FAMILIES = (
    ("Contact", "contact", "name", "string", "Mira", ""),
    ("Recipe", "recipe", "servings", "positiveInteger", "4", "-2"),
    ("Order", "order", "quantity", "positiveInteger", "8", "none"),
)


def documents(index):
    title, root, field, kind, good, bad = FAMILIES[index]
    schema = f'<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"><xs:element name="{root}"><xs:complexType><xs:sequence><xs:element name="{field}" type="xs:{kind}"/></xs:sequence></xs:complexType></xs:element></xs:schema>'
    valid = f"<{root}>\n  <{field}>{good}</{field}>\n</{root}>"
    invalid = (
        f"<{root}>\n  <unexpected/>\n</{root}>"
        if index == 0
        else f"<{root}>\n  <{field}>{bad}</{field}>\n</{root}>"
    )
    return schema, valid, invalid


def safe_xml(text):
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.I):
        raise ValueError("DTD and entity declarations are not allowed")
    element = ET.fromstring(text)
    for node in element.iter():
        local = node.tag.rsplit("}", 1)[-1] if isinstance(node.tag, str) else ""
        if local in {"include", "import", "redefine"}:
            raise ValueError("External schema composition is not allowed")
        for name in node.attrib:
            if name.rsplit("}", 1)[-1] in {
                "schemaLocation",
                "noNamespaceSchemaLocation",
            }:
                raise ValueError("External schema references are not allowed")
    return element


def build(qt):
    core, gui, patterns = qt.QtCore, qt.QtGui, qt.QtXmlPatterns
    with owned(qt, "Schema validation") as (handle, layout):
        family, variant = gui.QComboBox(handle.widget), gui.QComboBox(handle.widget)
        family.addItems([row[0] for row in FAMILIES])
        variant.addItems(["Valid", "Invalid"])
        schema_edit, xml_edit = (
            gui.QTextEdit(handle.widget),
            gui.QTextEdit(handle.widget),
        )
        schema_edit.setReadOnly(True)
        status = gui.QLabel("", handle.widget)
        for item in (family, variant, schema_edit, xml_edit, status):
            layout.addWidget(item)
        state = {"valid": None, "diagnostic": "", "line": 0, "column": 0}

        class Messages(patterns.QAbstractMessageHandler):
            def handleMessage(self, kind, description, identifier, location):
                state.update(
                    diagnostic=re.sub("<[^>]*>", "", str(description)),
                    line=int(value(location, "line")),
                    column=int(value(location, "column")),
                )

        messages = Messages(handle.widget)

        class XmlColorizer(gui.QSyntaxHighlighter):
            def highlightBlock(self, text):
                text = str(text)
                for pattern, color in (
                    (r"</?[^>]+>", "#315c93"),
                    (r"\b[\w:]+(?=\s*=)", "#8b4c99"),
                    (r'"[^"]*"|\x27[^\x27]*\x27', "#986126"),
                ):
                    form = gui.QTextCharFormat()
                    form.setForeground(gui.QBrush(gui.QColor(color)))
                    for match in re.finditer(pattern, text):
                        self.setFormat(match.start(), len(match.group()), form)
                inside = self.previousBlockState() == 1
                offset = 0 if inside else text.find("<!--")
                while offset >= 0:
                    end = text.find("-->", offset)
                    stop = len(text) if end < 0 else end + 3
                    form = gui.QTextCharFormat()
                    form.setForeground(gui.QBrush(gui.QColor("#758474")))
                    self.setFormat(offset, stop - offset, form)
                    inside = end < 0
                    if inside:
                        break
                    offset = text.find("<!--", stop)
                self.setCurrentBlockState(1 if inside else 0)

        highlighters = [
            XmlColorizer(value(edit, "document")) for edit in (schema_edit, xml_edit)
        ]
        for highlighter in highlighters:
            handle.cleanup.append(lambda item=highlighter: item.setDocument(None))

        def clear(*args):
            state.update(valid=None, diagnostic="", line=0, column=0)
            xml_edit.setExtraSelections([])
            status.setText("Edited; validate to check")

        def mark_line():
            xml_edit.setExtraSelections([])
            if state["line"] > 0:
                selection = gui.QTextEdit.ExtraSelection()
                selection.cursor = gui.QTextCursor(
                    value(xml_edit, "document").findBlockByNumber(state["line"] - 1)
                )
                selection.format.setBackground(gui.QBrush(gui.QColor("#ffd6ce")))
                selection.format.setProperty(gui.QTextFormat.FullWidthSelection, True)
                xml_edit.setExtraSelections([selection])

        def validate(*args):
            clear()
            schema_text, text = (
                str(schema_edit.toPlainText()),
                str(xml_edit.toPlainText()),
            )
            try:
                safe_xml(schema_text)
                safe_xml(text)
                schema = patterns.QXmlSchema()
                schema.setMessageHandler(messages)
                if not schema.load(
                    core.QByteArray(schema_text.encode("utf-8")),
                    core.QUrl("urn:fontlab:owned-schema"),
                ):
                    state["valid"] = False
                else:
                    validator = patterns.QXmlSchemaValidator(schema)
                    validator.setMessageHandler(messages)
                    state["valid"] = bool(
                        validator.validate(
                            core.QByteArray(text.encode("utf-8")),
                            core.QUrl("urn:fontlab:owned-instance"),
                        )
                    )
            except ET.ParseError as error:
                state.update(
                    valid=False,
                    diagnostic=str(error),
                    line=error.position[0],
                    column=error.position[1] + 1,
                )
            except ValueError as error:
                state.update(valid=False, diagnostic=str(error))
            if state["valid"]:
                state.update(diagnostic="", line=0, column=0)
                status.setText("Valid XML instance")
            else:
                status.setText(
                    f"Invalid: {state['diagnostic']} (line {state['line']}, column {state['column']})"
                )
                mark_line()

        def select_instance(*args):
            schema, valid, invalid = documents(int(value(family, "currentIndex")))
            schema_edit.setPlainText(schema)
            xml_edit.setPlainText(
                valid if int(value(variant, "currentIndex")) == 0 else invalid
            )
            validate()

        def select_family(*args):
            variant.setCurrentIndex(0)
            select_instance()

        wire(handle, xml_edit, "textChanged()", clear)
        wire(handle, variant, "currentIndexChanged(int)", select_instance)
        wire(handle, family, "currentIndexChanged(int)", select_family)
        button(qt, handle, layout, "Validate", validate)
        handle.controls.update(
            schema=schema_edit,
            instance=xml_edit,
            family=family,
            variant=variant,
            status=status,
            validate=validate,
            messages=messages,
            highlighters=highlighters,
        )
        handle.inspect_ui = lambda: dict(state)
        select_family()
        return handle
