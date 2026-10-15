# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/bf3b39a8c2df8e94.md
# this_file: ports/itemviews/pyqt-official/spreadsheet-bf3b39a8c2df8e94.py

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

import ast
import operator
import re


def address(row, col):
    return chr(65 + col) + str(row + 1)


def position(text):
    match = re.fullmatch(r"([A-F])(10|[1-9])", text.upper())
    if not match:
        raise ValueError("Use a cell from A1 through F10")
    return int(match[2]) - 1, ord(match[1]) - 65


def calculate(formulas, key, visiting=None):
    visiting = set() if visiting is None else set(visiting)
    if key in visiting:
        raise ValueError("Circular reference")
    visiting.add(key)
    text = formulas.get(key, "").strip()
    if not text:
        return 0.0
    if not text.startswith("="):
        try:
            return float(text)
        except ValueError:
            return text
    expression = text[1:].upper()

    def total(match):
        a, b = position(match[1]), position(match[2])
        values = []
        for row in range(min(a[0], b[0]), max(a[0], b[0]) + 1):
            for col in range(min(a[1], b[1]), max(a[1], b[1]) + 1):
                val = calculate(formulas, address(row, col), visiting)
                if isinstance(val, (int, float)):
                    values.append(val)
        return repr(sum(values))

    expression = re.sub(
        r"SUM\(([A-F](?:10|[1-9])):([A-F](?:10|[1-9]))\)", total, expression
    )
    tree = ast.parse(expression, mode="eval")
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in [int, float]:
            return node.value
        if isinstance(node, ast.Name):
            position(node.id)
            return calculate(formulas, node.id, visiting)
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](
                float(evaluate(node.left)), float(evaluate(node.right))
            )
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            return (
                -float(evaluate(node.operand))
                if isinstance(node.op, ast.USub)
                else float(evaluate(node.operand))
            )
        raise ValueError("Unsupported formula")

    return evaluate(tree.body)


def build(qt):
    with S.Session(qt, "Small expense spreadsheet") as s:
        s.vertical()
        status = s.keep("current", s.label("A1"))
        formula = s.line("formula")
        table = s.table("table", list("ABCDEF"), [[""] * 6 for _ in range(10)])
        formulas = {
            "A1": "Item",
            "B1": "Cost",
            "C1": "Count",
            "D1": "Total",
            "A2": "Paper",
            "B2": "12.5",
            "C2": "3",
            "D2": "=B2*C2",
            "A3": "Ink",
            "B3": "9",
            "C3": "2",
            "D3": "=B3*C3",
            "D4": "=SUM(D2:D3)",
        }
        busy = [False]

        def refresh():
            busy[0] = True
            results = {}
            try:
                for row in range(10):
                    for col in range(6):
                        key = address(row, col)
                        text = formulas.get(key, "")
                        try:
                            result = calculate(formulas, key)
                            display = (
                                format(result, ".12g")
                                if isinstance(result, (int, float))
                                else str(result)
                            )
                        except (
                            ValueError,
                            ZeroDivisionError,
                            SyntaxError,
                            TypeError,
                            OverflowError,
                        ):
                            display = "#ERROR"
                        if not text:
                            display = ""
                        item = table.item(row, col)
                        if item is None:
                            item = s.g.QTableWidgetItem("")
                            table.setItem(row, col, item)
                        item.setText(display)
                        results[key] = display
                s.state["results"] = results
                s.state["formulas"] = dict(formulas)
            finally:
                busy[0] = False

        def selection(row, col, *args):
            if not 0 <= row < 10 or not 0 <= col < 6:
                return
            key = address(row, col)
            status.setText(key)
            formula.setText(formulas.get(key, ""))
            s.state["current"] = key

        def changed(row, col):
            if busy[0]:
                return
            key = address(row, col)
            formulas[key] = str(S.value(table.item(row, col), "text"))
            refresh()
            selection(row, col)

        def entry(*args):
            key = s.state.get("current", "A1")
            formulas[key] = str(S.value(formula, "text"))
            refresh()

        s.link(table, "cellChanged(int,int)", changed)
        s.link(table, "currentCellChanged(int,int,int,int)", selection)
        s.link(formula, "returnPressed()", entry)

        def operation(op):
            dialog = s.keep("operation_dialog", s.alert(s.g.QDialog(s.window)))
            layout = s.vertical(dialog)
            cells = [address(r, c) for r in range(10) for c in range(6)]
            left = s.combo("left", cells, layout)
            right = s.combo("right", cells, layout)
            out = s.combo("output", cells, layout)

            def apply():
                a = str(S.value(left, "currentText"))
                b = str(S.value(right, "currentText"))
                target = str(S.value(out, "currentText"))
                formulas[target] = (
                    "=SUM(" + a + ":" + b + ")" if op == "Sum" else "=" + a + op + b
                )
                refresh()
                dialog.hide()

            s.button("apply_operation", "Apply", apply, layout)
            dialog.open()

        def clear():
            indexes = S.value(table, "selectedIndexes")
            for index in indexes:
                formulas.pop(address(index.row(), index.column()), None)
            refresh()

        def formatting(kind):
            dialog = s.alert(
                (s.g.QFontDialog if kind == "font" else s.g.QColorDialog)(s.window)
            )

            def apply(*args):
                for index in S.value(table, "selectedIndexes"):
                    item = table.item(index.row(), index.column())
                    if kind == "font":
                        item.setFont(dialog.selectedFont())
                    else:
                        item.setBackground(s.g.QBrush(dialog.selectedColor()))

            s.link(dialog, "accepted()", apply)
            dialog.open()

        class Currency(s.g.QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                obj = s.g.QDoubleSpinBox(parent)
                obj.setRange(-1000000.0, 1000000.0)
                obj.setDecimals(2)
                return obj

            def setEditorData(self, obj, index):
                try:
                    obj.setValue(
                        float(formulas.get(address(index.row(), index.column()), "0"))
                    )
                except ValueError:
                    obj.setValue(0.0)

            def setModelData(self, obj, model, index):
                formulas[address(index.row(), index.column())] = str(
                    S.value(obj, "value")
                )
                refresh()

        class Date(s.g.QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                obj = s.g.QDateEdit(parent)
                obj.setCalendarPopup(True)
                obj.setDisplayFormat(s.state.get("date_format", "yyyy-MM-dd"))
                return obj

            def setModelData(self, obj, model, index):
                formulas[address(index.row(), index.column())] = str(
                    S.value(obj, "date").toString(
                        s.state.get("date_format", "yyyy-MM-dd")
                    )
                )
                refresh()

        table.setItemDelegateForColumn(1, s.keep("currency_delegate", Currency(table)))
        table.setItemDelegateForColumn(4, s.keep("date_delegate", Date(table)))

        def print_table():
            printer = s.keep("printer", s.g.QPrinter())
            dialog = s.alert(s.g.QPrintDialog(printer, s.window))

            def accepted(*args):
                painter = s.g.QPainter(printer)
                try:
                    table.render(painter)
                finally:
                    painter.end()

            s.link(dialog, "accepted()", accepted)
            dialog.open()

        s.menu("File", [("Print", print_table), ("Exit", s.h.close)])
        menu = s.menu(
            "Cell",
            [(op, lambda key=op: operation(key)) for op in ["+", "-", "*", "/", "Sum"]]
            + [
                ("Clear", clear),
                ("Font", lambda: formatting("font")),
                ("Color", lambda: formatting("color")),
                ("ISO dates", lambda: s.state.update(date_format="yyyy-MM-dd")),
                ("Short dates", lambda: s.state.update(date_format="dd/MM/yyyy")),
            ],
        )
        table.setContextMenuPolicy(s.c.Qt.CustomContextMenu)
        s.link(
            table,
            "customContextMenuRequested(QPoint)",
            lambda pos: menu.popup(table.mapToGlobal(pos)),
        )
        s.menu(
            "Help",
            [
                (
                    "About",
                    lambda: s.state.update(
                        help="Formulas use A1 through F10, arithmetic, and SUM ranges."
                    ),
                )
            ],
        )
        refresh()
        selection(0, 0)
        s.keep("formulas", formulas)
        s.keep("recalculate", refresh)
        return s.h
